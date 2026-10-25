"""Read release-test metadata from an explicit original facade source authority."""

import hashlib
import json
import re
import tarfile
import tomllib
from email.parser import BytesParser
from pathlib import Path, PurePosixPath

METADATA_FILES = ("pyproject.toml", "uv.lock")
AUTHORITY_FIELDS = {
    "schema",
    "kind",
    "project",
    "source",
    "base_revision",
    "archive",
    "archive_sha256",
    "archive_files",
    "version",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def metadata(source):
    return {name: (source / name).read_bytes() for name in METADATA_FILES}


def archive_payload(archive):
    files = {}
    roots = set()
    with tarfile.open(archive) as stream:
        for member in stream:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or "\\" in member.name:
                raise ValueError("Unsafe original release archive path")
            if not path.parts:
                raise ValueError("Empty original release archive path")
            roots.add(path.parts[0])
            if member.isdir():
                continue
            if not member.isfile() or len(path.parts) < 2:
                raise ValueError("Original release archive contains a link or invalid member")
            name = PurePosixPath(*path.parts[1:]).as_posix()
            if name in files:
                raise ValueError("Original release archive contains duplicate members")
            files[name] = stream.extractfile(member).read()
    if len(roots) != 1 or not files:
        raise ValueError("Original release archive must have one complete source root")
    return files


def source_inventory(source):
    if source.is_symlink():
        raise ValueError("Original release source cannot be a link")
    files = {}
    for path in source.rglob("*"):
        if path.is_symlink():
            raise ValueError("Original release source contains a link")
        if path.is_file():
            files[path.relative_to(source).as_posix()] = digest(path.read_bytes())
        elif not path.is_dir():
            raise ValueError("Original release source contains a nonregular filesystem entry")
    return files


def verified_original(environment):
    record = json.loads(Path(environment["SHACL_RELEASE_PROJECT_AUTHORITY"]).read_text())
    if (
        set(record) != AUTHORITY_FIELDS
        or type(record["schema"]) is not int
        or record["schema"] != 1
        or record["kind"] != "original-facade-release-metadata"
        or record["project"] != "pyshacl-turbo"
    ):
        raise ValueError("Invalid original facade release metadata authority")
    receipt_path = Path(environment["SHACL_CANDIDATE_RECEIPT"]).resolve(strict=True)
    receipt = json.loads(receipt_path.read_text())
    revision = environment["SHACL_BASE_REVISION"]
    if (
        not re.fullmatch(r"[0-9a-f]{40}", revision)
        or record["base_revision"] != revision
        or receipt["base_input"]["revision"] != revision
        or receipt.get("schema") != 1
        or receipt.get("kind") != "test-only-facade-candidate"
        or receipt.get("publishable") is not False
        or receipt.get("artifact_namespace") != "candidate-facade"
    ):
        raise ValueError("Original release metadata differs from the explicit facade base")
    relative = PurePosixPath(receipt["base_archive"])
    if relative.is_absolute() or ".." in relative.parts or "\\" in str(relative):
        raise ValueError("Invalid original facade base archive reference")
    archive = Path(record["archive"])
    source = Path(record["source"])
    if not archive.is_absolute() or not source.is_absolute():
        raise ValueError("Original release authority requires absolute source/archive paths")
    if archive.resolve(strict=True) != (receipt_path.parent / relative).resolve(strict=True):
        raise ValueError("Release metadata archive is not the original facade base archive")
    if record["archive_sha256"] != receipt["base_archive_sha256"] or (
        digest(archive.read_bytes()) != record["archive_sha256"]
    ):
        raise ValueError("Original facade base archive SHA256 changed")
    files = archive_payload(archive)
    hashes = {name: digest(data) for name, data in files.items()}
    if hashes != record["archive_files"] or source_inventory(source) != hashes:
        raise ValueError("Complete original release source/archive inventory changed")
    tracked = receipt["base_input"]["files"]
    if any(tracked.get(name) != hashes.get(name) for name in METADATA_FILES) or any(
        tracked[name] != checksum for name, checksum in hashes.items() if name in tracked
    ):
        raise ValueError("Original release archive differs from its exact Git base")
    project = tomllib.loads(files["pyproject.toml"].decode())["project"]
    package = BytesParser().parsebytes(files["PKG-INFO"])
    if (
        project["name"] != "pyshacl-turbo"
        or project["version"] != record["version"]
        or package["Name"] != project["name"]
        or package["Version"] != project["version"]
        or "+candidate." in project["version"]
    ):
        raise ValueError("Release metadata is not the original facade project/version")
    return {name: files[name] for name in METADATA_FILES}


def read_release_metadata(root, environment):
    """Separate original release inputs from an explicitly unpublishable candidate.

    The owner verifies the complete candidate bundle and freezes this authority
    before collection. Recheck the original archive, Git-covered inputs and full
    extracted source independently here; never resolve another input implicitly.
    """
    original = metadata(Path(root))
    project = tomllib.loads(original["pyproject.toml"].decode())["project"]
    candidate = "+candidate." in project["version"]
    selected = "SHACL_RELEASE_PROJECT_AUTHORITY" in environment
    if candidate or "SHACL_CANDIDATE_RECEIPT" in environment or selected:
        if not all(
            environment.get(name)
            for name in (
                "SHACL_RELEASE_PROJECT_AUTHORITY",
                "SHACL_CANDIDATE_RECEIPT",
                "SHACL_BASE_REVISION",
            )
        ):
            raise ValueError("Candidate release tests require explicit original metadata authority")
        return verified_original(environment)
    return original
