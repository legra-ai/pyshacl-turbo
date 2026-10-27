"""Derive the owned engine identity independently from verified source bytes.

The field framing and Cargo feature spelling match the existing public paired
comparison verifier; source ownership here is explicitly local, never a Git alias.
"""

import hashlib
import re
from pathlib import Path, PurePosixPath

FORKS = ("oxigraph", "oxrdf", "oxsdatatypes", "spargebra", "sparopt", "spareval", "fancy-regex")


def canonical(data):
    return data.replace(b"\r\n", b"\n")


def engine_inputs(root):
    implementation = (root / "src/revision.rs").read_text()
    paths = re.findall(
        r'include_bytes!\("([^\"]+)"\)', implementation.split("fn update_source", 1)[0]
    )
    actual = {
        path.relative_to(root / "src").as_posix()
        for path in (root / "src").rglob("*.rs")
        if not path.name.endswith("_tests.rs")
    }
    if (
        not paths
        or len(paths) != len(set(paths))
        or set(paths) != actual
        or any(
            PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts for name in paths
        )
    ):
        raise ValueError("Fingerprint must cover the complete engine implementation")
    return paths


def fork_identity(source, package, features):
    fork = Path(package["manifest_path"]).resolve().parent
    if package["source"] is not None or not fork.is_relative_to(source / "vendor"):
        raise ValueError("Expected archive-owned patched semantic dependencies")
    result = hashlib.sha256()

    def field(data):
        result.update(canonical(data) + b"\0")

    files = [fork / "Cargo.toml", fork / "build.rs", *(fork / "src").rglob("*.rs")]
    for path in sorted(files, key=lambda path: path.relative_to(fork).parts):
        field(path.relative_to(fork).as_posix().encode())
        field(path.read_bytes())
    field(b"@shared/turbo-source-identity.rs")
    field((fork.parent / "turbo-source-identity.rs").read_bytes())
    for feature in sorted(features, key=lambda value: value.upper().replace("-", "_")):
        key = "CARGO_FEATURE_" + feature.upper().replace("-", "_")
        if package["name"] == "oxigraph" and key in {
            "CARGO_FEATURE_ROCKSDB",
            "CARGO_FEATURE_ROCKSDB_DEBUG",
            "CARGO_FEATURE_ROCKSDB_PKG_CONFIG",
        }:
            continue
        field((key + "=1").encode())
    return result.hexdigest()


def derive(source, metadata):
    source = source.resolve()
    engines = [p for p in metadata["packages"] if p["name"] == "pyshacl-turbo-engine"]
    if (
        len(engines) != 1
        or engines[0]["source"] is not None
        or Path(engines[0]["manifest_path"]).resolve() != source / "crates/engine/Cargo.toml"
    ):
        raise ValueError("Expected the archive-owned local SHACL engine")
    root = source / "crates/engine"
    paths = engine_inputs(root)
    digest = hashlib.sha256(canonical((root / "Cargo.toml").read_bytes()))
    for name in paths:
        digest.update(name.encode() + b"\0" + canonical((root / "src" / name).read_bytes()) + b"\0")
    nodes = {node["id"]: node for node in metadata["resolve"]["nodes"]}
    identities = {}
    for name in FORKS:
        packages = [package for package in metadata["packages"] if package["name"] == name]
        if len(packages) != 1:
            raise ValueError(f"Expected one owned semantic dependency: {name}")
        package = packages[0]
        identity = fork_identity(source, package, nodes[package["id"]]["features"])
        identities[name] = identity
        digest.update(name.encode() + b"\0" + identity.encode() + b"\0")
    return {
        "engine_source": "crates/engine",
        "engine_source_count": len(paths),
        "engine_fingerprint": digest.hexdigest(),
        "dependency_fingerprints": identities,
    }
