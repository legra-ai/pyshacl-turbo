"""Restore the original source peers declared by a published owner's uv lock."""

import importlib.util
import json
import re
import tomllib
from pathlib import Path, PurePosixPath


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def locked_version(owner, project):
    registry = load("provider_registry")
    if project not in registry.PROJECTS:
        raise ValueError("Unsupported original source peer project")
    lock = tomllib.loads((owner / "uv.lock").read_text())
    packages = [package for package in lock["package"] if package["name"] == project]
    if len(packages) != 1:
        raise ValueError("Expected one locked original source peer")
    version = packages[0]["version"]
    if not re.fullmatch(registry.VERSION, version):
        raise ValueError("Expected an exact locked registry peer version")
    return version


def adjacent_peer(owner, project):
    if project not in load("provider_registry").PROJECTS:
        raise ValueError("Unsupported original source peer project")
    manifest = tomllib.loads((owner / "pyproject.toml").read_text())
    binding = manifest["tool"]["uv"]["sources"][project]
    path = PurePosixPath(binding["path"])
    if (
        binding.get("editable") is not True
        or len(path.parts) != 2
        or path.parts[0] != ".."
        or not re.fullmatch(re.escape(project) + r"(?:-[a-z0-9-]+)?", path.parts[1])
    ):
        raise ValueError("Expected one explicitly adjacent original source peer")
    return path.parts[1]


def original_peer(project, version, output):
    """Retain an exact locked companion's original registry source and byte proof."""
    registry = load("provider_registry")
    document = registry.metadata(version, project=project)
    entry = registry.select_source(document, project, version)
    output.mkdir(parents=True, exist_ok=False)
    (output / "registry.json").write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    originals = output / "originals"
    originals.mkdir()
    archive = registry.download(entry, originals)
    sha = entry["digests"]["sha256"]
    source = registry.extract(archive, output / "source", sha)
    files = registry.verify_extracted(archive, source, sha)
    manifest = tomllib.loads((source / "pyproject.toml").read_text())
    if manifest["project"]["name"] != project or manifest["project"]["version"] != version:
        raise ValueError("Original peer archive differs from its locked registry identity")
    return {
        "kind": "published-sdist",
        "project": project,
        "version": version,
        "archive": str(archive),
        "source": str(source),
        "sha256": sha,
        "files": files,
        "registry_document": str(output / "registry.json"),
    }


def restore(owner, facade, output):
    """Restore the published lock's peer, independently of current acceptance code."""
    owner, output = owner.resolve(strict=True), output.resolve(strict=True)
    if owner == output or not owner.is_relative_to(output):
        raise ValueError("Only the downloaded owner source may move inside its output cohort")
    facade_version = locked_version(owner, "pyshacl-turbo")
    owl_version = locked_version(owner, "owlrl-turbo")
    native_name = adjacent_peer(facade, "rdflib-turbo")
    facade_name = adjacent_peer(owner, "pyshacl-turbo")
    declared = original_peer("pyshacl-turbo", facade_version, output / "peers/pyshacl-turbo")
    declared_source = Path(declared["source"]).resolve(strict=True)
    if adjacent_peer(declared_source, "rdflib-turbo") != native_name:
        raise ValueError("Published declaration peer names a different native source peer")
    if not declared_source.is_relative_to(output):
        raise ValueError("Downloaded declaration peer is outside its output cohort")
    owl = original_peer("owlrl-turbo", owl_version, output / "peers/owlrl-turbo")
    cohort = output / "cohort"
    cohort.mkdir()
    native = cohort / native_name
    declaration = cohort / facade_name
    owner.rename(native)
    declared_source.rename(declaration)
    return {
        "provider_source": str(native),
        "declaration_peer": {**declared, "source": str(declaration)},
        "owlrl": owl,
    }
