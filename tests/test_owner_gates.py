"""All Rust verification executes inside the actual native owner's authority."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

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
    assert command[-3:] == ["scripts.allocation_budgets", "--yaml-authority", str(authority)]


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
        str(yaml_authority),
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


@pytest.mark.parametrize("fail_allocation", [False, True])
def test_execute_persists_and_launches_the_same_original_yaml_command(
    tmp_path, monkeypatch, fail_allocation
):
    module = helper()
    owner, output = tmp_path / "owner", tmp_path / "output"
    owner.mkdir()
    output.mkdir()
    (owner / "rust-toolchain.toml").write_text('[toolchain]\nchannel="1.99.1"\n')
    for name in (
        "scripts/fmt.sh",
        "scripts/vendor_evaluator_tests.py",
        "scripts/vendor_dataset_tests.py",
        "scripts/allocation_budgets.py",
        "tests/build-metadata/Cargo.toml",
        "tests/store-contract/Cargo.toml",
    ):
        target = owner / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
    authority = tmp_path / "original yaml.json"
    authority.write_text("{}")
    receipt = output / "native-owner-coverage.json"
    launched = []

    def run(command, *, directory, env):
        record = json.loads(receipt.read_text())
        entry = record["gates"][-1]
        assert entry["status"] == "running"
        assert entry["command"] == command
        assert all(type(argument) is str for argument in command)
        assert directory == owner
        launched.append(entry["name"])
        if entry["name"] == "allocation":
            assert command[-2:] == ["--yaml-authority", str(authority)]
            if fail_allocation:
                raise subprocess.CalledProcessError(17, command)

    loader = SimpleNamespace(exec_module=lambda _: None)
    monkeypatch.setattr(module.importlib.util, "spec_from_file_location", lambda *_: loader)
    monkeypatch.setattr(
        module.importlib.util, "module_from_spec", lambda _: SimpleNamespace(run=run)
    )
    loader.loader = loader
    context = {
        "owner": owner,
        "output": output,
        "project": tmp_path / "project",
        "environment": {},
        "receipt": {
            "provider": {
                "source_sha256": "source",
                "native_wheel_sha256": "wheel",
                "identity": {"engine_fingerprint": "fingerprint"},
                "peers": {"yaml_test_dependency": {"authority": str(authority)}},
            }
        },
    }
    if fail_allocation:
        with pytest.raises(subprocess.CalledProcessError) as failure:
            module.execute(context, "coverage")
        assert failure.value.returncode == 17
    else:
        module.execute(context, "coverage")
    assert launched == [
        "format",
        "clippy",
        "metadata",
        "datatype",
        "evaluator",
        "dataset",
        "storage",
        "allocation",
    ]
    final = json.loads(receipt.read_text())["gates"]
    assert all(entry["status"] == "success" for entry in final[:-1])
    assert final[-1]["status"] == ("failed" if fail_allocation else "success")
    assert final[-1]["returncode"] == (17 if fail_allocation else 0)
