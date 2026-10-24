"""Compatibility keeps every gate on the exact installed registry pair."""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def helper():
    spec = importlib.util.spec_from_file_location(
        "compatibility_owner", ROOT / "scripts/provider_validation.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def context(tmp_path):
    output = tmp_path / "validation"
    output.mkdir()
    return {
        "acceptance": tmp_path / "frozen-source",
        "project": tmp_path / "installed-project",
        "output": output,
        "environment": {"PYTHONDONTWRITEBYTECODE": "1"},
    }


def test_compatibility_commands_keep_all_existing_gates_in_the_isolated_project(tmp_path):
    module, state = helper(), context(tmp_path)
    commands = dict(module.compatibility_commands(state))
    assert set(commands) == {"w3c", "upstream", "direct"}
    prefix = [
        "uv",
        "run",
        "--project",
        state["project"],
        "--locked",
        "--no-sync",
        "python",
        "-I",
        "-B",
    ]
    assert all(command[: len(prefix)] == prefix for command in commands.values())
    w3c = commands["w3c"]
    for path in ("tests/test_w3c.py", "tests/test_w3c_documents.py"):
        assert state["acceptance"] / path in w3c
    assert str(state["acceptance"] / "tests/test_sparql.py") + "::test_w3c_sparql_constraint" in w3c
    assert "--import-mode=importlib" in w3c
    assert f"--junitxml={state['output'] / 'w3c-results.xml'}" in w3c
    assert commands["upstream"][-2:] == ["--output", state["output"] / "upstream-results.json"]
    direct = commands["direct"]
    assert (
        direct[direct.index("--baseline") + 1] == state["acceptance"] / "docs/direct-contract.json"
    )
    assert direct[direct.index("--installed-pair") + 1] == state["output"] / "installed-pair.json"
    assert direct[direct.index("--output") + 1] == state["output"] / "direct-contract.json"


def test_each_compatibility_stage_rechecks_runtime_and_source_authority(tmp_path, monkeypatch):
    module, state = helper(), context(tmp_path)
    calls, verified = [], []
    monkeypatch.setattr(module, "run", lambda command, **kwargs: calls.append((command, kwargs)))
    monkeypatch.setattr(module, "verify_sources", lambda value: verified.append(value))
    module.compatibility(state)
    assert len(calls) == 3
    assert verified == [state] * 4
    for _, arguments in calls:
        assert arguments["directory"] == state["acceptance"]
        assert arguments["env"]["COVERAGE_FILE"] == str(state["output"] / "python.coverage")
    stages = json.loads((state["output"] / "compatibility-stages.json").read_text())["stages"]
    assert [(entry["name"], entry["status"]) for entry in stages] == [
        ("w3c", "success"),
        ("upstream", "success"),
        ("direct", "success"),
    ]


def test_failed_upstream_gate_stops_before_direct_contract_and_keeps_its_failure(
    tmp_path, monkeypatch
):
    module, state = helper(), context(tmp_path)
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        if len(commands) == 2:
            raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(module, "run", run)
    monkeypatch.setattr(module, "verify_sources", lambda value: None)
    with pytest.raises(subprocess.CalledProcessError):
        module.compatibility(state)
    assert len(commands) == 2
    stages = json.loads((state["output"] / "compatibility-stages.json").read_text())["stages"]
    assert [(entry["name"], entry["status"]) for entry in stages] == [
        ("w3c", "success"),
        ("upstream", "failed"),
    ]
    assert stages[-1]["returncode"] == 1


def test_workflow_uses_original_pure_archives_and_registry_pair_instead_of_source_install():
    steps = yaml.safe_load((ROOT / ".github/workflows/compatibility.yml").read_text())["jobs"][
        "compatibility"
    ]["steps"]
    commands = "\n".join(step.get("run", "") for step in steps)
    assert "make dev" not in commands
    assert "make test-compatibility" not in commands
    assert "uv sync" not in commands
    assert 'uv build --sdist --out-dir "$RUNNER_TEMP/facade-dist"' in commands
    assert (
        'uv build --wheel --out-dir "$RUNNER_TEMP/facade-wheel" "$RUNNER_TEMP"/facade-dist/*.tar.gz'
        in commands
    )
    assert "python -B scripts/provider_validation.py" in commands
    assert "--suite compatibility" in commands
    assert '--facade-source "$GITHUB_WORKSPACE"' in commands
    assert '--output "$RUNNER_TEMP/compatibility-validation"' in commands
    assert any(step.get("with", {}).get("toolchain") == "1.99.1" for step in steps)
    artifacts = [
        step["with"]["path"]
        for step in steps
        if step.get("uses", "").startswith("actions/upload-artifact@")
    ]
    assert len(artifacts) == 1
    assert "${{ runner.temp }}/compatibility-validation/" in artifacts[0]
