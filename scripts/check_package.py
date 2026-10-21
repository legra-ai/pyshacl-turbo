"""Check the actual distribution, including vendored sources needed to rebuild it."""

import argparse
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path


def check(path):
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        metadata_names = [name for name in files if name.endswith(".dist-info/METADATA")]
        assert len(metadata_names) == 1
        metadata = BytesParser().parsebytes(files[metadata_names[0]])
        prefix = metadata_names[0].removesuffix("METADATA") + "licenses/"
        assert any(name.endswith((".so", ".pyd")) for name in files), "Native extension missing"
        assert "pyshacl_turbo/assets/shacl-shacl.ttl" in files
        assert files["pyshacl_turbo/py.typed"] == b"", "Inline typing marker missing"
    else:
        with tarfile.open(path) as archive:
            files = {
                member.name.split("/", 1)[1]: archive.extractfile(member).read()
                for member in archive.getmembers()
                if member.isfile()
            }
        metadata = BytesParser().parsebytes(files["PKG-INFO"])
        prefix = ""
        for name in [
            "Cargo.lock",
            "uv.lock",
            "Cargo.toml",
            "pyproject.toml",
            "python/pyshacl_turbo/py.typed",
            "rust-toolchain.toml",
            "crates/engine/src/lib.rs",
            "crates/engine/src/architecture.svg",
            "crates/engine/src/architecture.md",
            "crates/engine/tests/pipeline.rs",
            "crates/python/src/lib.rs",
            "tests/test_release.py",
            "scripts/smoke_wheel.py",
            "vendor/fancy-regex-0.19.2/src/lib.rs",
            "vendor/oxigraph-0.5.11/src/lib.rs",
            "vendor/oxrdf-0.3.4/src/lib.rs",
            "vendor/oxsdatatypes-0.2.3/src/lib.rs",
            "vendor/spargebra-0.4.7/src/lib.rs",
            "vendor/sparopt-0.3.7/src/lib.rs",
            "vendor/spareval-0.2.7/src/lib.rs",
            "vendor/turbo-source-identity.rs",
        ]:
            assert name in files, f"Source distribution cannot be verified/rebuilt: missing {name}"
        for vendor in (
            "oxigraph-0.5.11",
            "oxrdf-0.3.4",
            "oxsdatatypes-0.2.3",
            "spargebra-0.4.7",
            "sparopt-0.3.7",
            "spareval-0.2.7",
        ):
            for name in ("build.rs", "src/source_identity.rs"):
                assert f"vendor/{vendor}/{name}" in files, (
                    f"Missing compiled identity: {vendor}/{name}"
                )
        assert ".cargo/config.toml" not in files, "Repository hook opt-in must not ship"
        assert "crates/engine/build.rs" not in files, "Repository hook installer must not ship"
    assert metadata["Name"] == "pyshacl-turbo"
    assert metadata["License-Expression"] == "MIT OR Apache-2.0"
    for name in ["LICENSE-MIT", "LICENSE-APACHE"]:
        assert files[prefix + name] == (Path(__file__).parents[1] / name).read_bytes()
        for vendor in [
            "oxigraph-0.5.11",
            "oxrdf-0.3.4",
            "oxsdatatypes-0.2.3",
            "spargebra-0.4.7",
            "sparopt-0.3.7",
            "spareval-0.2.7",
        ]:
            assert prefix + f"vendor/{vendor}/{name}" in files, f"Missing {vendor} attribution"
    assert not any("CHANGELOG" in name for name in files), "Generated changelog must not ship"
    assert not any("/target/" in name or "/.venv/" in name for name in files)
    print(f"Verified {path.name}: metadata, licenses and packaged files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path)
    for archive in parser.parse_args().archives:
        check(archive)
