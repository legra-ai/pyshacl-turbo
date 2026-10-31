"""Restore the original source peers declared by a published owner's uv lock."""

import importlib.util
import json
import re
import sys
import tomllib
from pathlib import Path, PurePosixPath


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_companion(owner):
    """Use the verifier shipped by the already verified original native owner."""
    path = owner / "scripts/pure_companion.py"
    spec = importlib.util.spec_from_file_location("verified_owner_companion", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_declaration(owner):
    """Load only the declaration builder shipped by the verified native owner."""
    path = owner / "scripts/declaration_peer.py"
    spec = importlib.util.spec_from_file_location("verified_owner_declaration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_yaml(owner):
    """Require the YAML authority helper shipped by this verified original owner."""
    path = owner / "scripts/yaml_test_inputs.py"
    if not path.is_file():
        raise TypeError("Verified native owner lacks its required YAML test-input helper")
    spec = importlib.util.spec_from_file_location("verified_owner_yaml_inputs", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not all(
        callable(getattr(module, name, None)) for name in ("prepare", "verify", "verify_loaded")
    ):
        raise TypeError("Verified native owner lacks required YAML authority capabilities")
    return module


def verify_yaml_test_dependency(owner, dependency):
    """Bind the portable dependency record to the owner's explicit original inputs."""
    verified = load_yaml(owner).verify(owner, Path(dependency["authority"]))
    if verified["record"] != dependency["record"]:
        raise ValueError("YAML test dependency differs from its retained original authority")
    return verified


def prepare_yaml_test_dependency(owner, output):
    """Build one original pure test wheel from the verified owner's frozen lock."""
    record = load_yaml(owner).prepare(owner, output, "3.13.16")
    dependency = {"authority": str(output / "yaml-inputs.json"), "record": record}
    verify_yaml_test_dependency(owner, dependency)
    return dependency


def verify_declaration_peer(owner, record, *, initial=True):
    """A Git export peer and an installed registry facade have distinct roles."""
    if (
        not isinstance(record, dict)
        or record.get("role") != "uv-export-declaration"
        or record.get("project") != "pyshacl-turbo"
        or record.get("authority", {}).get("kind") != "git"
        or record.get("version") != locked_version(owner, "pyshacl-turbo")
    ):
        raise ValueError("Expected the exact locked Git declaration authority")
    load_declaration(owner).verify(owner, record, initial=initial)
    return record


def prepare_declaration_peer(owner, output):
    """Retain an original UV sdist from the owner's independent declaration Git role."""
    record = load_declaration(owner).prepare(owner, output, sys.executable)
    return verify_declaration_peer(owner, record)


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


def original_peer(project, version, output, *, owner=None):
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
    result = {
        "kind": "published-sdist",
        "project": project,
        "version": version,
        "archive": str(archive),
        "source": str(source),
        "sha256": sha,
        "files": files,
        "registry_document": str(output / "registry.json"),
    }
    if project == "owlrl-turbo":
        if owner is None:
            raise ValueError("Original OWL wheel verification requires its explicit native owner")
        entry = registry.select_universal(document, project, version)
        wheel = registry.download(entry, originals)
        payload = load_companion(owner).verify_payload(source, wheel)
        result.update(
            wheel=str(wheel),
            wheel_sha256=entry["digests"]["sha256"],
            package_payload=payload,
        )
    return result


def execution_owl_version(consumer):
    """Require one exact consumer test pin, independently of the owner's build lock."""
    manifest = tomllib.loads((consumer / "pyproject.toml").read_text())
    requirements = manifest.get("project", {}).get("optional-dependencies", {}).get("test", [])
    candidates = [value for value in requirements if re.match(r"(?i)^owlrl[-_.]turbo\b", value)]
    if len(candidates) != 1:
        raise ValueError("Expected one exact consumer OWL test dependency")
    match = re.fullmatch(r"owlrl-turbo==(" + load("provider_registry").VERSION + ")", candidates[0])
    if match is None:
        raise ValueError("Expected one unconditional exact registry OWL test dependency")
    return match[1]


def execution_peer(consumer, owner, output):
    """Restore selected execution authority without changing original build peers."""
    return original_peer("owlrl-turbo", execution_owl_version(consumer), output, owner=owner)


def verify_owl_peer(owner, owl):
    """Reattest each independently named build or execution original without relabeling."""
    registry = load("provider_registry")
    if (
        registry.verify_extracted(
            Path(owl["archive"]), Path(owl["source"]), owl["sha256"], exact_inventory=False
        )
        != owl["files"]
    ):
        raise ValueError("Original OWL source changed during validation")
    if (
        load("provider_validation").digest(Path(owl["wheel"])) != owl["wheel_sha256"]
        or load_companion(owner).verify_payload(Path(owl["source"]), Path(owl["wheel"]))
        != owl["package_payload"]
    ):
        raise ValueError("Original OWL wheel changed during validation")


def restore(owner, output):
    """Restore the published lock's peer, independently of current acceptance code."""
    owner, output = owner.resolve(strict=True), output.resolve(strict=True)
    if owner == output or not owner.is_relative_to(output):
        raise ValueError("Only the downloaded owner source may move inside its output cohort")
    owl_version = locked_version(owner, "owlrl-turbo")
    native_name = tomllib.loads((owner / "pyproject.toml").read_text())["project"]["name"]
    if native_name != "rdflib-turbo":
        raise ValueError("Expected the original native provider project identity")
    facade_name = adjacent_peer(owner, "pyshacl-turbo")
    declared = prepare_declaration_peer(owner, output / "peers/pyshacl-turbo")
    declared_source = Path(declared["source"]).resolve(strict=True)
    if adjacent_peer(declared_source, "rdflib-turbo") != native_name:
        raise ValueError("Git declaration peer names a different native source peer")
    if not declared_source.is_relative_to(output):
        raise ValueError("Git declaration peer is outside its output cohort")
    owl = original_peer("owlrl-turbo", owl_version, output / "peers/owlrl-turbo", owner=owner)
    cohort = output / "cohort"
    cohort.mkdir()
    native = cohort / native_name
    declaration = cohort / facade_name
    owner.rename(native)
    declared_source.rename(declaration)
    declared = {**declared, "source": str(declaration)}
    verify_declaration_peer(native, declared)
    yaml = prepare_yaml_test_dependency(native, output / "peers/yaml-test-dependency")
    return {
        "provider_source": str(native),
        "declaration_peer": declared,
        "owlrl": owl,
        "yaml_test_dependency": yaml,
    }
