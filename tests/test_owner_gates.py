"""All Rust verification executes inside the actual native owner's authority."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


def helper():
    path = Path(__file__).resolve().parents[1] / "scripts/owner_gates.py"
    spec = importlib.util.spec_from_file_location("owner_gates", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_allocation_gate_passes_the_explicit_original_yaml_authority(tmp_path):
    (tmp_path / "rust-toolchain.toml").write_text('[toolchain]\nchannel="1.99.1"\n')
    authority = tmp_path / "original-yaml-inputs.json"
    command = dict(helper().commands(tmp_path, "coverage", yaml_authority=authority))["allocation"]
    assert command[-3:] == ["scripts.allocation_budgets", "--yaml-authority", authority]


def test_allocation_gate_rejects_missing_yaml_before_launch(tmp_path):
    (tmp_path / "rust-toolchain.toml").write_text('[toolchain]\nchannel="1.99.1"\n')
    with pytest.raises(ValueError, match="explicit original YAML authority"):
        helper().commands(tmp_path, "coverage", yaml_authority=None)


def test_owner_verification_preserves_all_native_gate_families(tmp_path):
    owner = tmp_path / "actual-owner"
    owner.mkdir()
    (owner / "rust-toolchain.toml").write_text('[toolchain]\nchannel="1.99.1"\n')
    yaml_authority = tmp_path / "yaml-inputs.json"
    commands = dict(helper().commands(owner, "coverage", yaml_authority=yaml_authority))
    assert set(commands) == {
        "format",
        "clippy",
        "metadata",
        "datatype",
        "evaluator",
        "dataset",
        "storage",
        "allocation",
    }
    assert commands["clippy"] == [
        "cargo",
        "+1.99.1",
        "clippy",
        "--workspace",
        "--lib",
        "--tests",
        "--locked",
        "--",
        "-D",
        "warnings",
    ]
    assert commands["datatype"] == [
        "cargo",
        "+1.99.1",
        "test",
        "--locked",
        "-p",
        "oxsdatatypes",
        "--lib",
    ]
    assert commands["evaluator"][-1] == "scripts.vendor_evaluator_tests"
    assert commands["dataset"][-1] == "scripts.vendor_dataset_tests"
    assert commands["allocation"][-3:] == [
        "scripts.allocation_budgets",
        "--yaml-authority",
        yaml_authority,
    ]
    assert commands["storage"] == ["make", "test-store-contract"]
    assert commands["metadata"] == ["make", "test-build-metadata"]


def test_existing_regex_gate_invokes_the_owners_actual_profile_runner(tmp_path):
    owner = tmp_path / "actual-owner"
    owner.mkdir()
    (owner / "rust-toolchain.toml").write_text('[toolchain]\nchannel="1.99.1"\n')
    assert dict(helper().commands(owner, "regex", yaml_authority=None))["regex"][-1] == (
        "scripts.vendor_regex_tests"
    )


def test_unknown_or_unpinned_owner_gate_fails_before_compilation(tmp_path):
    (tmp_path / "rust-toolchain.toml").write_text('[toolchain]\nchannel="stable"\n')
    with pytest.raises(ValueError, match="pinned compiler"):
        helper().commands(tmp_path, "coverage", yaml_authority=None)


def test_owner_gate_library_loads_without_a_source_path_override(tmp_path):
    path = Path(__file__).resolve().parents[1] / "scripts/owner_gates.py"
    subprocess.run([sys.executable, "-I", path], cwd=tmp_path, check=True, capture_output=True)
