"""The benchmark inventory and observed semantic differences stay reviewable."""

import gzip
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest
import yaml


def checker():
    path = Path(__file__).resolve().parents[1] / "benchmarks/check_companions.py"
    spec = importlib.util.spec_from_file_location("check_companions", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evidence():
    observation = {"query": {"rows": [["<urn:a>"]], "variables": ["x"]}}
    run = {
        "operation": "select",
        "nodes": 10,
        "comparison": {"status": "equal"},
        "backends": {
            name: {"observations": [observation], "memory_samples": [{"observation": observation}]}
            for name in ("reference", "turbo")
        },
    }
    baseline = {
        "cases": {
            "select/10": {
                "comparison": "equal",
                "backends": {
                    name: checker().fingerprint(observation) for name in ("reference", "turbo")
                },
            }
        }
    }
    return {"runs": [run]}, baseline


def test_previously_equal_results_cannot_silently_change():
    module = checker()
    report, baseline = evidence()
    module.check(report, baseline)
    changed = deepcopy(report)
    changed["runs"][0]["backends"]["turbo"]["memory_samples"][0]["observation"] = {"query": "wrong"}
    with pytest.raises(RuntimeError, match="observation changed"):
        module.check(changed, baseline)
    report["runs"][0]["comparison"]["status"] = "different"
    with pytest.raises(RuntimeError, match="lost full equality"):
        module.check(report, baseline)


def test_missing_or_duplicate_workloads_fail():
    module = checker()
    report, baseline = evidence()
    baseline["cases"]["ask/10"] = deepcopy(baseline["cases"]["select/10"])
    with pytest.raises(RuntimeError, match="inventory"):
        module.check(report, baseline)
    del baseline["cases"]["ask/10"]
    report["runs"].append(deepcopy(report["runs"][0]))
    with pytest.raises(RuntimeError, match="Duplicate"):
        module.check(report, baseline)


def test_checked_in_baseline_matches_all_original_observations():
    root = Path(__file__).resolve().parents[1] / "benchmarks"
    with gzip.open(root / "companions-baseline-run.json.gz", "rt") as source:
        report = json.load(source)
    baseline = json.loads((root / "companions-baseline.json").read_text())
    assert len(report["runs"]) == 32
    checker().check(report, baseline)


def test_companion_workflow_parses_and_executes_every_command_as_text():
    path = Path(__file__).resolve().parents[1] / ".github/workflows/companions.yml"
    workflow = yaml.safe_load(path.read_text())
    steps = workflow["jobs"]["benchmark"]["steps"]
    commands = [step["run"] for step in steps if "run" in step]
    assert all(isinstance(command, str) for command in commands)
    assert any("--only-binary :all:" in command for command in commands)
    assert any("check_companions.py" in command for command in commands)
