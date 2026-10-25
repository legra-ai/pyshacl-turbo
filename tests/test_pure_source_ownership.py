"""The pure façade retains no second native engine or native verification owner."""

import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_native_implementation_and_collector_belong_only_to_provider():
    for name in (
        "crates",
        "Cargo.toml",
        "Cargo.lock",
        "rust-toolchain.toml",
        "rustfmt-toolchain",
        ".cargo/config.toml",
        "native-coverage-sources.json",
        "scripts/native_coverage.py",
        "scripts/build_manylinux.sh",
        "scripts/build_manylinux_inner.sh",
        "scripts/fmt.sh",
        "tests/test_native_coverage.py",
        "tests/test_dependency_identity.py",
        "tests/test_coverage_dependencies.py",
        "tests/test_rhusky_build_root.py",
        "build.rs",
        "vendor/turbo-source-identity.rs",
    ):
        assert not (ROOT / name).exists(), f"Dormant native ownership remains: {name}"
    assert {path.name for path in (ROOT / "vendor").iterdir() if path.is_dir()} == {"pyshacl"}
    assert (ROOT / "vendor/pyshacl/LICENSE.txt").is_file()
    assert (ROOT / "scripts/provider_coverage.py").is_file()
    assert (ROOT / "scripts/owner_driver.py").is_file()


def test_original_facade_archive_contains_no_retired_native_build_subsystem(tmp_path):
    subprocess.run(
        ["uv", "build", "--sdist", "--no-sources", "--out-dir", str(tmp_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    (archive,) = tmp_path.glob("*.tar.gz")
    with tarfile.open(archive) as source:
        paths = {Path(*Path(member.name).parts[1:]) for member in source if member.isfile()}
    assert Path("python/pyshacl_turbo/__init__.py") in paths
    assert Path("scripts/owner_driver.py") in paths
    assert Path("tests/test_rhusky_build_root.py") not in paths
    assert not any(path.parts[0] in {"crates", ".cargo"} for path in paths)
    assert not any(path.name in {"Cargo.toml", "Cargo.lock", "build.rs"} for path in paths)
