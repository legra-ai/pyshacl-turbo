"""Run the sole native owner's collector against explicit frozen facade inputs.

This does not select a provider release or prove registry availability. Callers
must separately pass the registry capability prerequisite before publication.
No provider source, revision, collector identity or wheel has a default.
"""

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import tomllib
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_yaml_summary(owner, authority, record, summary, collector, environment):
    """Recheck the opaque loaded proof in the actual collector-owned environment."""
    if summary["yaml_inputs"] != record:
        raise ValueError("YAML summary differs from its exact original input authority")
    location = summary["yaml_environment"]
    project = Path(location["project"]).resolve(strict=True)
    venv = Path(location["venv"]).resolve(strict=True)
    base = (owner / "target/native-coverage/profiles").resolve(strict=True)
    if not project.is_relative_to(base):
        raise ValueError("YAML collector environment is outside its native owner")
    parts = project.relative_to(base).parts
    if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{32}", parts[0]) or parts[1] != "project":
        raise ValueError("YAML collector environment has the wrong owned profile layout")
    if venv != project / ".venv":
        raise ValueError("YAML collector environment has the wrong virtual environment")
    project_run = ["uv", "run", "--project", project, "--locked", "--no-sync"]
    actual = collector.verify_installed_yaml(owner, authority, project_run, venv, environment)
    if actual != summary["yaml_installed"]:
        raise ValueError("YAML installed summary differs from its complete loaded proof")


def git(source, *arguments):
    return subprocess.check_output(["git", "-C", str(source), *arguments], text=True).strip()


def freeze_tree(source, project):
    source = source.resolve(strict=True)
    if git(source, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError(f"{project} authority requires a clean source checkout")
    manifest = tomllib.loads((source / "pyproject.toml").read_text())
    if manifest["project"]["name"] != project:
        raise ValueError(f"Wrong source identity for {project}")
    files = {}
    for name in filter(None, git(source, "ls-files", "-z").split("\0")):
        path = source / name
        if not path.resolve(strict=True).is_relative_to(source):
            raise ValueError(f"{project} source escapes the frozen checkout")
        files[name] = digest(path)
    return {"revision": git(source, "rev-parse", "HEAD"), "files": files}


def freeze_owl_source(source, archive, sha256, *, initial=True):
    if (archive is None) != (sha256 is None):
        raise ValueError("Both OWL source archive and SHA-256 are required")
    if archive is None:
        return {"kind": "git", **freeze_tree(source, "owlrl-turbo")}
    spec = importlib.util.spec_from_file_location(
        "provider_registry", Path(__file__).with_name("provider_registry.py")
    )
    registry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(registry)
    files = registry.verify_extracted(archive, source, sha256, exact_inventory=initial)
    manifest = tomllib.loads((source / "pyproject.toml").read_text())
    if manifest["project"]["name"] != "owlrl-turbo":
        raise ValueError("Original OWL source has the wrong project identity")
    return {
        "kind": "published-sdist",
        "filename": archive.name,
        "sha256": sha256,
        "version": manifest["project"]["version"],
        "files": files,
    }


def source_id(authority):
    return (
        authority["revision"]
        if authority["kind"] == "git"
        else "sdist-sha256:" + authority["sha256"]
    )


def collector_authority(authority):
    return (
        {"kind": "git", "revision": authority["revision"]}
        if authority["kind"] == "git"
        else authority
    )


def verify_owl_inputs(owner, source, wheel):
    """Bind the complete original OWL wheel to its verified source and hash."""
    spec = importlib.util.spec_from_file_location(
        "verified_owner_companion", owner / "scripts/pure_companion.py"
    )
    companion = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(companion)
    return {
        "wheel_sha256": digest(wheel),
        "package_payload": companion.verify_payload(source, wheel),
    }


def verify_owner(source, revision, collector_sha256):
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("An explicit immutable provider revision is required")
    if not re.fullmatch(r"[0-9a-f]{64}", collector_sha256):
        raise ValueError("An explicit collector SHA-256 is required")
    frozen = freeze_tree(source, "rdflib-turbo")
    if frozen["revision"] != revision:
        raise ValueError("Provider source revision differs from its explicit authority")
    collector = source / "scripts/native_coverage.py"
    if frozen["files"].get("scripts/native_coverage.py") != collector_sha256:
        raise ValueError("Provider collector differs from its explicit authority")
    cargo = tomllib.loads((source / "Cargo.toml").read_text())
    if cargo["dependencies"]["pyshacl-turbo-engine"] != {"path": "crates/engine"}:
        raise ValueError("Native provider must own the local SHACL engine")
    if digest(collector) != collector_sha256:
        raise ValueError("Provider collector changed during verification")
    return frozen


def verify_source(source, revision, collector_sha256, archive, archive_sha256, *, initial=True):
    git_mode = revision is not None and archive is None and archive_sha256 is None
    archive_mode = revision is None and archive is not None and archive_sha256 is not None
    if not (git_mode or archive_mode):
        raise ValueError("Choose exactly one complete provider source authority")
    if git_mode:
        return {"kind": "git", **verify_owner(source, revision, collector_sha256)}
    if not re.fullmatch(r"[0-9a-f]{64}", collector_sha256):
        raise ValueError("An explicit collector SHA-256 is required")
    spec = importlib.util.spec_from_file_location(
        "provider_registry", Path(__file__).with_name("provider_registry.py")
    )
    registry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(registry)
    files = registry.verify_extracted(
        Path(archive), source, archive_sha256, exact_inventory=initial
    )
    manifest = tomllib.loads((source / "pyproject.toml").read_text())
    cargo = tomllib.loads((source / "Cargo.toml").read_text())
    if (
        manifest["project"]["name"] != "rdflib-turbo"
        or cargo["dependencies"]["pyshacl-turbo-engine"] != {"path": "crates/engine"}
        or files.get("scripts/native_coverage.py") != collector_sha256
    ):
        raise ValueError("Original archive does not match its native provider authority")
    return {
        "kind": "published-sdist",
        "filename": Path(archive).name,
        "sha256": archive_sha256,
        "version": manifest["project"]["version"],
        "files": files,
    }


def collector_command(
    owner,
    facade,
    wheel,
    owlrl,
    output,
    python,
    *,
    archive=None,
    archive_sha256=None,
    candidate=None,
    owlrl_archive=None,
    owlrl_sha256=None,
    owlrl_wheel,
    yaml_authority,
):
    command = [
        "uv",
        "run",
        "--no-project",
        "--python",
        python,
        "python",
        str(owner / "scripts/native_coverage.py"),
        "--python",
        python,
        "--shacl-source",
        str(facade),
        "--shacl-wheel",
        str(wheel),
        "--owlrl-source",
        str(owlrl),
        "--owlrl-wheel",
        str(owlrl_wheel),
        "--yaml-authority",
        str(yaml_authority),
        "--output",
        str(output),
    ]
    if (archive is None) != (archive_sha256 is None):
        raise ValueError("Both original source archive and SHA-256 are required")
    if archive is not None:
        if candidate is not None:
            raise ValueError("Test-only facade candidates cannot use a published provider")
        command.extend(["--source-archive", str(archive), "--source-sha256", archive_sha256])
    if candidate is not None:
        command.extend(
            [
                "--shacl-candidate-receipt",
                str(candidate["receipt"]),
                "--shacl-base-revision",
                candidate["facade_revision"],
            ]
        )
    if (owlrl_archive is None) != (owlrl_sha256 is None):
        raise ValueError("Both OWL source archive and SHA-256 are required")
    if owlrl_archive is not None:
        command.extend(["--owlrl-archive", str(owlrl_archive), "--owlrl-sha256", owlrl_sha256])
    return command


def measure(args):
    owner = args.provider_source.resolve(strict=True)
    facade = args.facade_source.resolve(strict=True)
    wheel = args.facade_wheel.resolve(strict=True)
    owlrl = args.owlrl_source.resolve(strict=True)
    owlrl_wheel = args.owlrl_wheel.resolve(strict=True)
    yaml_authority = args.yaml_authority.resolve(strict=True)
    output = args.output.resolve()
    if any(output.is_relative_to(source) for source in (owner, facade, owlrl)):
        raise ValueError("Coverage output must be outside all frozen source checkouts")
    provider = verify_source(
        owner,
        args.provider_revision,
        args.collector_sha256,
        args.source_archive,
        args.source_sha256,
    )
    owl = freeze_owl_source(owlrl, args.owlrl_archive, args.owlrl_sha256)
    owl_inputs = verify_owl_inputs(owner, owlrl, owlrl_wheel)
    yaml_helper = load("published_peers").load_yaml(owner)
    yaml_inputs = yaml_helper.verify(owner, yaml_authority)["record"]
    yaml_authority_sha256 = digest(yaml_authority)
    spec = importlib.util.spec_from_file_location(
        "verified_provider_collector", owner / "scripts/native_coverage.py"
    )
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    if not callable(getattr(collector, "verify_installed_yaml", None)):
        raise TypeError("Verified native collector lacks required YAML loaded-payload verification")
    candidate = collector.candidate_parameters(
        provider,
        args.shacl_candidate_receipt,
        args.shacl_base_revision,
        tomllib.loads((owner / "pyproject.toml").read_text())["project"]["version"],
    )
    acceptance = collector.freeze_facade_inputs(facade, wheel, candidate=candidate)
    command = collector_command(
        owner,
        facade,
        wheel,
        owlrl,
        output,
        args.python,
        archive=args.source_archive,
        archive_sha256=args.source_sha256,
        candidate=candidate,
        owlrl_archive=args.owlrl_archive,
        owlrl_sha256=args.owlrl_sha256,
        owlrl_wheel=owlrl_wheel,
        yaml_authority=yaml_authority,
    )
    receipt = {
        "provider": provider,
        "facade": acceptance,
        "owlrl": owl,
        "owlrl_inputs": owl_inputs,
        "yaml_test_dependency": {"authority": str(yaml_authority), "record": yaml_inputs},
        "yaml_authority_sha256": yaml_authority_sha256,
        "command": command,
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "provider-authority.json").write_text(json.dumps(receipt, indent=2) + "\n")
    try:
        subprocess.run(command, check=True)
    finally:
        if yaml_helper.verify(owner, yaml_authority)["record"] != yaml_inputs or (
            digest(yaml_authority) != yaml_authority_sha256
        ):
            raise ValueError("Original YAML authority changed during native measurement")
    if (
        verify_source(
            owner,
            args.provider_revision,
            args.collector_sha256,
            args.source_archive,
            args.source_sha256,
            initial=False,
        )
        != provider
    ):
        raise ValueError("Provider source changed during native measurement")
    if freeze_owl_source(owlrl, args.owlrl_archive, args.owlrl_sha256, initial=False) != owl:
        raise ValueError("OWL-RL source changed during native measurement")
    if verify_owl_inputs(owner, owlrl, owlrl_wheel) != owl_inputs:
        raise ValueError("Original OWL wheel changed during native measurement")
    collector.verify_facade_inputs(facade, wheel, acceptance, candidate=candidate)
    summary = json.loads((output / "summary.json").read_text())
    verify_yaml_summary(
        owner,
        yaml_authority,
        yaml_inputs,
        summary,
        collector,
        load("provider_validation").environment(),
    )
    if (
        summary["project"] != "rdflib-turbo"
        or summary["revision"] != source_id(provider)
        or summary["source_authority"] != collector_authority(provider)
        or summary["owlrl_revision"] != source_id(owl)
        or summary["owlrl_source_authority"] != collector_authority(owl)
        or summary["owlrl_inputs"] != owl_inputs
        or summary["owlrl_wheel_sha256"] != owl_inputs["wheel_sha256"]
        or summary["harness_sha256"] != args.collector_sha256
        or summary["shacl_inputs"] != acceptance
        or summary["shacl_revision"]
        != acceptance.get("source_authority", {}).get("base_revision", acceptance["revision"])
        or not summary["source_sha256"]
        or any(provider["files"].get(name) != sha for name, sha in summary["source_sha256"].items())
        or set(summary["stages"]) != {"rust", "python", "shacl", "owlrl", "combined"}
    ):
        raise ValueError("Native measurement does not match its provider authority")
    (output / "provider-authority-verified.json").write_text(json.dumps(receipt, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider-source", type=Path, required=True)
    parser.add_argument("--provider-revision")
    parser.add_argument("--source-archive", type=Path)
    parser.add_argument("--source-sha256")
    parser.add_argument("--collector-sha256", required=True)
    parser.add_argument("--facade-source", type=Path, required=True)
    parser.add_argument("--facade-wheel", type=Path, required=True)
    parser.add_argument("--shacl-candidate-receipt", type=Path)
    parser.add_argument("--shacl-base-revision")
    parser.add_argument("--owlrl-source", type=Path, required=True)
    parser.add_argument("--owlrl-archive", type=Path)
    parser.add_argument("--owlrl-sha256")
    parser.add_argument("--owlrl-wheel", type=Path, required=True)
    parser.add_argument("--yaml-authority", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--python", default="3.13")
    measure(parser.parse_args())


if __name__ == "__main__":
    main()
