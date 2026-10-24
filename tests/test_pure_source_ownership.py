"""The pure façade retains no second native engine or native verification owner."""

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
        "vendor/turbo-source-identity.rs",
    ):
        assert not (ROOT / name).exists(), f"Dormant native ownership remains: {name}"
    assert {path.name for path in (ROOT / "vendor").iterdir() if path.is_dir()} == {"pyshacl"}
    assert (ROOT / "vendor/pyshacl/LICENSE.txt").is_file()
    assert (ROOT / "scripts/provider_coverage.py").is_file()
    assert (ROOT / "scripts/owner_driver.py").is_file()
