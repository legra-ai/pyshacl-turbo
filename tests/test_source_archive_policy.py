"""Pure facade archives retain verification inputs without installing Git hooks."""

import subprocess
import sys
import tarfile
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def source_archive_files(tmp_path_factory):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path_factory.mktemp("verified-source")
    subprocess.run(
        ["uv", "build", "--sdist", "--python", sys.executable, "--out-dir", str(output)],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    (source,) = output.glob("*.tar.gz")
    with tarfile.open(source) as archive:
        files = {
            entry.name.split("/", 1)[1]: archive.extractfile(entry).read()
            for entry in archive.getmembers()
            if entry.isfile()
        }
    return root, files


def test_source_archive_preserves_verification_inputs_without_repository_hooks(
    source_archive_files,
):
    root, files = source_archive_files
    assert ".cargo/config.toml" not in files
    assert "crates/engine/build.rs" not in files
    expected = (
        "uv.lock",
        "pyproject.toml",
        "python/pyshacl_turbo/_native.py",
        "python/pyshacl_turbo/py.typed",
        "scripts/check_package.py",
        "scripts/owner_driver.py",
        "scripts/provider_coverage.py",
        "vendor/pyshacl/LICENSE.txt",
        "vendor/pyshacl-issue-70.patch",
        "tests/test_source_archive_policy.py",
        "docs/native-coverage.md",
        ".github/workflows/ci.yml",
    )
    for name in expected:
        assert files[name] == (root / name).read_bytes(), name
    assert not any("CHANGELOG" in name or "/target/" in name for name in files)


def test_source_distribution_uses_uv_lock_without_legacy_dependency_snapshots(source_archive_files):
    root, files = source_archive_files
    assert files["uv.lock"] == (root / "uv.lock").read_bytes()
    assert any(name.startswith("scripts/") for name in files)
    for name in ("requirements-test.in", "requirements-test.lock"):
        assert not (root / name).exists()
        assert name not in files


def test_facade_source_archive_has_no_dormant_native_implementation(source_archive_files):
    _, files = source_archive_files
    assert not any(name.startswith("crates/") for name in files)
    native_vendor = (
        "oxigraph-",
        "oxrdf-",
        "oxsdatatypes-",
        "spargebra-",
        "sparopt-",
        "spareval-",
        "fancy-regex-",
    )
    assert not any(
        name.startswith(tuple("vendor/" + prefix for prefix in native_vendor)) for name in files
    )
    assert not any(
        name in files
        for name in (
            "Cargo.toml",
            "Cargo.lock",
            "rust-toolchain.toml",
            "rustfmt-toolchain",
            "native-coverage-sources.json",
            "vendor/turbo-source-identity.rs",
        )
    )
