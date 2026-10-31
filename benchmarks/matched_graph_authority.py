"""Original registry wheels, native-UV locks and isolated benchmark identities."""

import hashlib
import importlib.util
import itertools
import json
import re
import shutil
import tomllib
from email.parser import Parser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def load(name, directory="benchmarks"):
    spec = importlib.util.spec_from_file_location(name, ROOT / directory / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RELEASES = load("releases")
REGISTRY = load("provider_registry", "scripts")


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def cohort_key(wheels):
    """All resolved original wheel identities, not only the three top-level pins."""
    if not wheels or any(
        not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) for row in wheels.values()
    ):
        raise ValueError("Missing original wheel cohort hashes")
    vector = sorted((name, row["version"], row["sha256"]) for name, row in wheels.items())
    return hashlib.sha256(json.dumps(vector).encode()).hexdigest()


def installed_identity():
    from importlib.metadata import distributions

    result = RELEASES.identity()
    result["wheel_tags"] = {}
    for dist in distributions():
        name = dist.metadata["Name"].lower().replace("_", "-")
        result["wheel_tags"][name] = (
            Parser().parsestr(dist.read_text("WHEEL") or "").get_all("Tag", [])
        )
    return result


def identity(project, python, driver):
    result = json.loads(
        RELEASES.command(
            [
                "uv",
                "run",
                "--project",
                project,
                "--python",
                python,
                "--locked",
                "--no-sync",
                "--no-build",
                "python",
                "-I",
                "-B",
                driver,
                "--identity",
            ]
        )
    )
    result["uv_lock_sha256"] = sha(project / "uv.lock")
    return result


def setup(environment, directory, python, driver, lock=None):
    project = directory / environment["id"]
    if lock is None:
        RELEASES.setup(environment, directory, None, python)
    else:
        if project.exists():
            raise ValueError("Locked replay requires a fresh project")
        RELEASES.command(
            ["uv", "init", "--bare", "--no-workspace", "--vcs", "none", "--python", python, project]
        )
        RELEASES.command(["uv", "python", "pin", "--project", project, python])
        manifest = project / "pyproject.toml"
        dependencies = [name + version for name, version in environment["requirements"].items()]
        text = manifest.read_text()
        if text.count("dependencies = []") != 1:
            raise RuntimeError("Unexpected native-UV bare project declaration")
        manifest.write_text(
            text.replace("dependencies = []", "dependencies = " + json.dumps(dependencies))
            + '\n[tool.uv]\nprerelease = "allow"\n'
        )
        shutil.copyfile(lock, project / "uv.lock")
        RELEASES.command(
            [
                "uv",
                "sync",
                "--project",
                project,
                "--python",
                python,
                "--locked",
                "--no-build",
                "--prerelease",
                "allow",
            ]
        )
        if sha(lock) != sha(project / "uv.lock"):
            raise RuntimeError("Native-UV changed the supplied replay lock")
    return project, identity(project, python, driver)


def _tags(filename):
    fields = filename.removesuffix(".whl").rsplit("-", 3)
    if not filename.endswith(".whl") or len(fields) != 4:
        raise ValueError("Expected a locked original wheel filename")
    return {
        "-".join(parts) for parts in itertools.product(*(field.split(".") for field in fields[-3:]))
    }


def _retain(record, directory):
    filename = unquote(urlsplit(record["url"]).path).split("/")[-1]
    entry = {
        "filename": filename,
        "url": record["url"],
        "digests": {"sha256": record["hash"].removeprefix("sha256:")},
    }
    path = directory / filename
    if path.exists():
        REGISTRY.verify_original(path, entry["digests"]["sha256"])
    else:
        REGISTRY.download(entry, directory)
    return path


def capture_originals(project, installed, directory):
    """Bind every installed payload to the UV-locked original wheel bytes."""
    directory.mkdir(parents=True, exist_ok=True)
    lock = tomllib.loads((project / "uv.lock").read_text())
    wheels = {}
    for name, package in installed["packages"].items():
        matches = [
            row
            for row in lock["package"]
            if row["name"] == name and row["version"] == package["version"]
        ]
        if (
            len(matches) != 1
            or matches[0].get("source") != {"registry": "https://pypi.org/simple"}
            or package["origin"] is not None
        ):
            raise ValueError(
                "Matched cohorts require original PyPI distributions without source overrides"
            )
        selected = matches[0]
        tags = set(installed["wheel_tags"][name])
        candidates = [
            row
            for row in selected.get("wheels", [])
            if _tags(unquote(urlsplit(row["url"]).path).split("/")[-1]) == tags
        ]
        if len(candidates) != 1:
            raise ValueError("The installed wheel tags do not select one locked original")
        path = _retain(candidates[0], directory)
        with ZipFile(path) as archive:
            for member in archive.namelist():
                if member.endswith(("/", ".dist-info/RECORD")):
                    continue  # UV rewrites RECORD; whole installed identity is guarded separately.
                if (
                    package["payload_sha256"].get(member)
                    != hashlib.sha256(archive.read(member)).hexdigest()
                ):
                    raise RuntimeError("Installed payload differs from its original registry wheel")
        wheels[name] = {
            "version": package["version"],
            "sha256": sha(path),
            "file": path.name,
            "url": candidates[0]["url"],
        }
        if name in RELEASES.TURBO | RELEASES.REFERENCE:
            _retain(selected["sdist"], directory)
    return wheels
