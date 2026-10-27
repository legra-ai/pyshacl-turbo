"""Select and retain exact original PyPI provider files, without source guesses."""

import hashlib
import itertools
import json
import re
import shutil
import tarfile
import tomllib
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen

VERSION = r"\d+\.\d+\.\d+(?:(?:a|b|rc)\d+)?"
PROJECTS = {"rdflib-turbo", "pyshacl-turbo", "owlrl-turbo"}


def select_source(document, project, version):
    """Select a companion's exact original source rather than guessing a Git ref."""
    if (
        project not in PROJECTS
        or not re.fullmatch(VERSION, version)
        or document["info"]["name"] != project
        or document["info"]["version"] != version
    ):
        raise ValueError("Registry identity differs from the exact companion source pin")
    filename = project.replace("-", "_") + f"-{version}.tar.gz"
    sources = [
        entry
        for entry in document["urls"]
        if entry["packagetype"] == "sdist" and entry["filename"] == filename
    ]
    if len(sources) != 1:
        raise ValueError("Expected one original source archive for the exact companion")
    return sources[0]


def select_universal(document, project, version):
    """Select only the exact locked pure companion wheel in its original registry record."""
    select_source(document, project, version)
    filename = project.replace("-", "_") + f"-{version}-py3-none-any.whl"
    wheels = [
        entry
        for entry in document["urls"]
        if entry["packagetype"] == "bdist_wheel" and entry["filename"] == filename
    ]
    if len(wheels) != 1:
        raise ValueError("Expected one original universal wheel for the exact companion")
    return wheels[0]


def declared_version(manifest):
    project = tomllib.loads(manifest.read_text())["project"]
    providers = [
        value
        for value in project["dependencies"]
        if re.match(r"rdflib[-_]turbo\b", value, re.IGNORECASE)
    ]
    if len(providers) != 1:
        raise ValueError("Coverage requires one exact runtime provider pin")
    match = re.fullmatch(rf"rdflib[-_]turbo\s*==\s*({VERSION})", providers[0], re.IGNORECASE)
    if match is None:
        raise ValueError("Coverage requires one exact runtime provider pin")
    return match.group(1)


def wheel_tags(filename):
    if not filename.endswith(".whl"):
        raise ValueError("Expected an original wheel filename")
    fields = filename[:-4].split("-")
    if len(fields) not in (5, 6) or fields[0] != "rdflib_turbo":
        raise ValueError("Expected a native provider wheel filename")
    return {"-".join(parts) for parts in itertools.product(*(s.split(".") for s in fields[-3:]))}


def select(document, version, installed_tags):
    if (
        document["info"]["name"] != "rdflib-turbo"
        or document["info"]["version"] != version
        or not installed_tags
    ):
        raise ValueError("PyPI provider identity differs from the exact runtime pin")
    sources = [
        entry
        for entry in document["urls"]
        if entry["packagetype"] == "sdist" and entry["filename"] == f"rdflib_turbo-{version}.tar.gz"
    ]
    wheels = [
        entry
        for entry in document["urls"]
        if entry["packagetype"] == "bdist_wheel"
        and wheel_tags(entry["filename"]) == installed_tags
        and entry["filename"].split("-")[1] == version
    ]
    if len(sources) != 1 or len(wheels) != 1:
        raise ValueError("Expected one original source archive and selected wheel")
    return sources[0], wheels[0]


def verify_original(path, expected_sha256):
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError("Missing SHA-256 for original registry file")
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"Hash differs from original registry file: {path.name}")


def metadata(version, *, project="rdflib-turbo"):
    if project not in PROJECTS or not re.fullmatch(VERSION, version):
        raise ValueError("Expected an exact companion project and version")
    with urlopen(f"https://pypi.org/pypi/{project}/{version}/json", timeout=60) as response:
        return json.load(response)


def download(entry, directory):
    filename = entry["filename"]
    parsed = urlsplit(entry["url"])
    if (
        Path(filename).name != filename
        or "\\" in filename
        or parsed.scheme != "https"
        or parsed.netloc != "files.pythonhosted.org"
        or parsed.query
        or parsed.fragment
        or unquote(parsed.path).split("/")[-1] != filename
    ):
        raise ValueError("Expected an original PyPI file URL")
    target = directory / filename
    with urlopen(entry["url"], timeout=60) as response, target.open("xb") as destination:
        final = urlsplit(response.geturl())
        if final.scheme != "https" or final.netloc != "files.pythonhosted.org":
            raise ValueError("Original PyPI file redirected outside the registry file service")
        shutil.copyfileobj(response, destination)
    verify_original(target, entry["digests"]["sha256"])
    return target


def extract(archive, destination, expected_sha256):
    verify_original(archive, expected_sha256)
    destination.mkdir(parents=True, exist_ok=False)
    prefix = None
    # bounded: one name per file in this package's fixed original source archive.
    files = set()
    with tarfile.open(archive, "r:gz") as package:
        for member in package:
            name = member.name.rstrip("/") if member.isdir() else member.name
            path = PurePosixPath(name)
            if (
                path.is_absolute()
                or "\\" in name
                or any(part in ("", ".", "..") for part in name.split("/"))
                or (not member.isdir() and not member.isfile())
                or (not member.isdir() and len(path.parts) < 2)
                or (prefix is not None and path.parts[0] != prefix)
                or (member.isfile() and name in files)
            ):
                raise ValueError(f"Invalid original source archive member: {member.name!r}")
            prefix = path.parts[0]
            target = destination.joinpath(*path.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with package.extractfile(member) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output)
            files.add(name)
    if prefix is None or not files:
        raise ValueError("Original provider source archive has no files")
    return destination / prefix


def verify_extracted(archive, source, expected_sha256, *, exact_inventory=True):
    verify_original(archive, expected_sha256)
    root = source.resolve(strict=True)
    prefix = None
    # bounded: one hash per file in the fixed original provider package.
    files = {}
    with tarfile.open(archive, "r:gz") as package:
        for member in package:
            if member.isdir():
                continue
            path = PurePosixPath(member.name)
            relative = str(PurePosixPath(*path.parts[1:]))
            if (
                not member.isfile()
                or path.is_absolute()
                or "\\" in member.name
                or len(path.parts) < 2
                or any(part in ("", ".", "..") for part in member.name.split("/"))
                or (prefix is not None and path.parts[0] != prefix)
                or relative in files
            ):
                raise ValueError("Invalid original source archive member")
            prefix = path.parts[0]
            target = root.joinpath(*path.parts[1:])
            if (
                not target.resolve(strict=True).is_relative_to(root)
                or target.is_symlink()
                or any(
                    parent.is_symlink() for parent in target.parents if parent.is_relative_to(root)
                )
            ):
                raise ValueError("Extracted source escapes its original archive")
            with package.extractfile(member) as original, target.open("rb") as actual:
                expected = hashlib.file_digest(original, "sha256").hexdigest()
                if hashlib.file_digest(actual, "sha256").hexdigest() != expected:
                    raise ValueError(f"Source bytes differ from original archive: {relative}")
            files[relative] = expected
    if not files:
        raise ValueError("Extracted source inventory differs from its original archive")
    if exact_inventory:
        actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
        if actual != set(files):
            raise ValueError("Extracted source inventory differs from its original archive")
    return files
