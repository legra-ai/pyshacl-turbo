"""Check a local declaration and an explicitly supplied native source owner."""

import argparse
import re
import tomllib
from pathlib import Path


def declaration(facade):
    facade = Path(facade).resolve(strict=True)
    manifest = tomllib.loads((facade / "pyproject.toml").read_text())
    if manifest["project"]["name"] != "pyshacl-turbo":
        raise ValueError("Expected the facade source project")
    source = manifest["tool"]["uv"]["sources"]["rdflib-turbo"]
    relative = source["path"]
    if source != {"path": relative, "editable": True} or not relative.startswith("../"):
        raise ValueError("Expected an explicit sibling editable provider declaration")
    lock = tomllib.loads((facade / "uv.lock").read_text())
    packages = [p for p in lock["package"] if p["name"] == "rdflib-turbo"]
    if len(packages) != 1 or packages[0]["source"] != {"editable": relative}:
        raise ValueError("Provider lock source differs from the explicit declaration")
    requirements = [
        re.fullmatch(r"rdflib-turbo==([A-Za-z0-9.+!-]+)", text)
        for text in manifest["project"]["dependencies"]
        if text.startswith("rdflib-turbo")
    ]
    if len(requirements) != 1 or requirements[0] is None:
        raise ValueError("Expected exactly one pinned provider runtime requirement")
    # A native uv source override resolves the explicit editable project's
    # actual version independently of the published registry requirement.
    return {
        "relative_path": relative,
        "version": packages[0]["version"],
        "registry_version": requirements[0].group(1),
    }


def verify(facade, provider):
    """The caller supplies its arranged or independently audited source authority."""
    declared = declaration(facade)
    provider = Path(provider).resolve(strict=True)
    project = tomllib.loads((provider / "pyproject.toml").read_text())["project"]
    if project["name"] != "rdflib-turbo" or project["version"] != declared["version"]:
        raise ValueError("Explicit provider identity differs from the facade declaration")
    cargo = tomllib.loads((provider / "Cargo.toml").read_text())
    if cargo["dependencies"]["pyshacl-turbo-engine"] != {"path": "crates/engine"}:
        raise ValueError("The explicit provider must own the local shared engine")
    library = (provider / "crates/engine/src/lib.rs").resolve(strict=True)
    if not library.is_file() or not library.is_relative_to(provider):
        raise ValueError("The engine source must remain inside the explicit owner")
    return {**declared, "provider_source": str(provider)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--facade-source", type=Path, required=True)
    parser.add_argument("--provider-source", type=Path, required=True)
    args = parser.parse_args()
    verify(args.facade_source, args.provider_source)


if __name__ == "__main__":
    main()
