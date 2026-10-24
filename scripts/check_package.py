"""Check the actual distribution, including its pure Python rebuild and owner-verification inputs."""

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
        assert not any(
            name.endswith((".so", ".pyd", ".dylib", ".dll")) or ".so." in name for name in files
        ), "Facade wheel must not contain native libraries"
        wheel_metadata = BytesParser().parsebytes(
            files[metadata_names[0].removesuffix("METADATA") + "WHEEL"]
        )
        assert wheel_metadata["Root-Is-Purelib"] == "true", "Facade wheel must be pure Python"
        assert wheel_metadata.get_all("Tag") == ["py3-none-any"], "Facade wheel must be universal"
        assert "pyshacl_turbo/_native.py" in files, "Shared native provider facade missing"
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
            "uv.lock",
            "pyproject.toml",
            "python/pyshacl_turbo/py.typed",
            "python/pyshacl_turbo/_native.py",
            "tests/test_release.py",
            "scripts/smoke_wheel.py",
            "scripts/provider_validation.py",
            "scripts/provider_coverage.py",
            "scripts/owner_driver.py",
            "scripts/provider_registry.py",
            "vendor/pyshacl/LICENSE.txt",
        ]:
            assert name in files, f"Source distribution cannot be verified/rebuilt: missing {name}"
        assert not any(name.startswith("crates/") for name in files), (
            "Facade must not duplicate native source"
        )
        assert not any(
            name in files
            for name in (
                "Cargo.toml",
                "Cargo.lock",
                "rust-toolchain.toml",
                "rustfmt-toolchain",
                "native-coverage-sources.json",
            )
        ), "Facade must not contain dormant native build authority"
        assert not any(
            name.startswith("vendor/") and not name.startswith("vendor/pyshacl/") for name in files
        ), "Native dependencies belong to the provider source distribution"
        assert ".cargo/config.toml" not in files, "Repository hook opt-in must not ship"
    assert metadata["Name"] == "pyshacl-turbo"
    assert metadata["License-Expression"] == "MIT OR Apache-2.0"
    for name in ["LICENSE-MIT", "LICENSE-APACHE"]:
        assert files[prefix + name] == (Path(__file__).parents[1] / name).read_bytes()
    assert (
        files[prefix + "vendor/pyshacl/LICENSE.txt"]
        == (Path(__file__).parents[1] / "vendor/pyshacl/LICENSE.txt").read_bytes()
    )
    assert not any("CHANGELOG" in name for name in files), "Generated changelog must not ship"
    assert not any("/target/" in name or "/.venv/" in name for name in files)
    print(f"Verified {path.name}: metadata, licenses and packaged files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path)
    for archive in parser.parse_args().archives:
        check(archive)
