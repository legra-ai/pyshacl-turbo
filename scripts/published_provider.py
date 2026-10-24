"""Resolve original published provider authority before native measurement.

The declared registry pin is authoritative. Incapable releases fail before
compilation; candidate Git sources are handled by the separate explicit runner.
"""

import argparse
import email
import hashlib
import importlib.util
import json
import re
import subprocess
import tomllib
import zipfile
from pathlib import Path


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def write(path, record):
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


def verify_wheel(wheel, receipt):
    with zipfile.ZipFile(wheel) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError("Original provider wheel has duplicate records")
        payload = {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist()
            if name.startswith("rdflib_turbo/") and not name.endswith("/")
        }
        if payload != receipt["payload"]:
            raise ValueError("Original wheel differs from installed registry payload")
        metadata = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(metadata) != 1:
            raise ValueError("Expected exactly one original provider metadata record")
        document = email.message_from_bytes(archive.read(metadata[0]))
        if document["Name"] != "rdflib-turbo" or document["Version"] != receipt["provider"]:
            raise ValueError("Original wheel metadata differs from its installed registry receipt")
    return payload


def verify_source_package(
    owner, payload, native_member, *, package="rdflib_turbo", source_root=None
):
    if package not in {"rdflib_turbo", "pyshacl_turbo", "owlrl_turbo"}:
        raise ValueError("Unsupported turbo source package")
    root = owner / "python" / package if source_root is None else source_root
    if not root.resolve(strict=True).is_relative_to(owner.resolve(strict=True)):
        raise ValueError("Source package escapes its verified owner")
    # bounded: this provider's fixed source-package file inventory.
    source = {
        package + "/" + path.relative_to(root).as_posix(): digest(path)
        for path in root.rglob("*")
        if path.is_file()
    }
    if not source or source != {
        name: sha for name, sha in payload.items() if name != native_member
    }:
        raise ValueError("Published provider source package differs from its original wheel")


def metadata(owner):
    manifest = tomllib.loads((owner / "pyproject.toml").read_text())
    cargo = tomllib.loads((owner / "Cargo.toml").read_text())
    if cargo["dependencies"]["pyshacl-turbo-engine"] != {"path": "crates/engine"}:
        raise ValueError("Published provider does not own its local SHACL engine")
    maturin = manifest["tool"]["maturin"]
    if (
        manifest["build-system"]["requires"] != ["maturin==1.15.0"]
        or maturin["profile"] != "release"
        or maturin["locked"] is not True
        or set(maturin["features"]) != {"pyo3/extension-module", "persistence"}
    ):
        raise ValueError("Published provider differs from the tested native build profile")
    expected = tomllib.loads((owner / "rust-toolchain.toml").read_text())["toolchain"]["channel"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", expected):
        raise ValueError("Native source identity requires an exact pinned compiler")
    rustc = subprocess.run(
        ["rustc", "+" + expected, "-vV"], check=True, text=True, capture_output=True
    ).stdout
    if not rustc.startswith("rustc " + expected + " "):
        raise ValueError("Native source identity requires its exact pinned compiler")
    hosts = [
        line.removeprefix("host: ") for line in rustc.splitlines() if line.startswith("host: ")
    ]
    if len(hosts) != 1:
        raise ValueError("Pinned compiler did not report one native target")
    command = [
        "cargo",
        "+" + expected,
        "metadata",
        "--locked",
        "--format-version",
        "1",
        "--manifest-path",
        str(owner / "Cargo.toml"),
        "--filter-platform",
        hosts[0],
        "--features",
        ",".join(maturin["features"]),
    ]
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return json.loads(result.stdout), {"rustc": rustc, "command": command, "maturin": maturin}


def restore_source_identity(owner, facade, output, archive, sha256, expected_fingerprint):
    """Resolve identity at the final archive-faithful uv peer layout."""
    peers = load("published_peers").restore(owner, facade, output)
    owner = Path(peers["provider_source"])
    files = load("provider_registry").verify_extracted(archive, owner, sha256)
    resolved, profile = metadata(owner)
    write(output / "cargo-metadata.json", resolved)
    identity = load("provider_identity").derive(owner, resolved)
    if identity["engine_fingerprint"] != expected_fingerprint:
        raise ValueError("Published source identity differs from the installed native wheel")
    return {
        "source": owner,
        "files": files,
        "identity": identity,
        "profile": profile,
        "peers": peers,
    }


def resolve(source, wheel, output):
    source, wheel = source.resolve(strict=True), wheel.resolve(strict=True)
    registry = load("provider_registry")
    version = registry.declared_version(source / "pyproject.toml")
    output.mkdir(parents=True, exist_ok=False)
    request = {"provider_version": version, "facade_wheel_sha256": digest(wheel)}
    write(output / "request.json", request)
    # This real installed registry probe precedes source downloads and compilation.
    receipt = load("check_registry_pair").verify(wheel, receipt=True)
    if receipt["provider"] != version or receipt["engine_source"] != "crates/engine":
        raise ValueError("Registry capability does not match the declared owned provider")
    write(output / "registry-capability.json", receipt)
    header = email.message_from_string(receipt["wheel_metadata"])
    if header["Root-Is-Purelib"] != "false":
        raise ValueError("Published provider is not a native platform wheel")
    document = registry.metadata(version)
    write(output / "registry.json", document)
    archive_entry, wheel_entry = registry.select(document, version, set(header.get_all("Tag", [])))
    originals = output / "originals"
    originals.mkdir()
    archive, native_wheel = [
        registry.download(entry, originals) for entry in (archive_entry, wheel_entry)
    ]
    payload = verify_wheel(native_wheel, receipt)
    owner = registry.extract(archive, output / "source", archive_entry["digests"]["sha256"])
    verify_source_package(owner, payload, receipt["native_member"])
    restored = restore_source_identity(
        owner, source, output, archive, archive_entry["digests"]["sha256"], receipt["fingerprint"]
    )
    owner = restored["source"]
    collector = owner / "scripts/native_coverage.py"
    if not collector.is_file() or not (owner / "scripts/coverage_archive.py").is_file():
        raise ValueError("Published provider lacks its archive-authoritative native collector")
    result = {
        **request,
        "kind": "published-sdist",
        "source": str(owner),
        "source_archive": str(archive),
        "source_sha256": digest(archive),
        "native_wheel": str(native_wheel),
        "native_wheel_sha256": digest(native_wheel),
        "collector_sha256": digest(collector),
        "identity": restored["identity"],
        "profile": restored["profile"],
        "peers": restored["peers"],
    }
    write(output / "published-authority.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facade-source", type=Path, required=True)
    parser.add_argument("--facade-wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(resolve(arguments.facade_source, arguments.facade_wheel, arguments.output)))


if __name__ == "__main__":
    main()
