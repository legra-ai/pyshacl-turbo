"""Prevent version comparisons from inventing performance equivalence."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml


def module():
    path = Path(__file__).resolve().parents[1] / "benchmarks/releases.py"
    spec = importlib.util.spec_from_file_location("release_benchmarks", path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def measured(value, *, stable=True, ns=100):
    return {"observation": value, "stable": stable, "median_ns": ns}


def test_ratios_require_complete_stable_outputs_and_history_parity():
    bench = module()
    left = {
        "closure": {"ordinary": "same", "generalized": []},
        "report": {"graph": "report", "text": "same", "conforms": False},
    }
    right = {**left, "report": {"graph": "report", "text": "different", "conforms": False}}
    assert bench.compare_runs(measured(left), measured(left, ns=50))["speedup"] == 2
    assert bench.compare_runs(measured(left), measured(right))["speedup"] is None
    assert bench.compare_runs(measured(left), measured(left, stable=False))["speedup"] is None
    bench.require_standard_parity(measured(left), measured(right))
    changed = {**right, "report": {"graph": "changed", "text": "same", "conforms": False}}
    with pytest.raises(RuntimeError, match="report"):
        bench.require_standard_parity(measured(left), measured(changed))


def test_version_matrix_rejects_ambiguous_or_missing_products():
    bench = module()
    with pytest.raises(ValueError):
        bench.validate_matrix({"environments": []})
    with pytest.raises(ValueError):
        bench.validate_matrix(
            {
                "environments": [
                    {
                        "id": "reference",
                        "backend": "reference",
                        "requirements": {"rdflib": "==7.6.0"},
                    }
                ]
            }
        )


def test_workers_fail_fast_on_errors_and_timeouts():
    import sys

    bench = module()
    with pytest.raises(RuntimeError, match="failed"):
        bench.command([sys.executable, "-c", "raise SystemExit(7)"], timeout=10)
    with pytest.raises(RuntimeError, match="timeout"):
        bench.command([sys.executable, "-c", "import time; time.sleep(60)"], timeout=0.1)


def test_harness_identity_is_stable_when_started_through_a_symlink(tmp_path, monkeypatch):
    bench = module()
    link = tmp_path / "linked-release.py"
    link.symlink_to(bench.ROOT / "benchmarks/releases.py")
    monkeypatch.setattr(bench, "__file__", str(link))
    hashes = bench.harness_hashes()
    assert set(hashes) == {
        "benchmarks/releases.py",
        "benchmarks/companions.py",
        "benchmarks/inference_fanout.py",
        "benchmarks/fanout_availability.py",
        "tests/upstream_support/process_launch.py",
    }


@pytest.mark.parametrize("no_config", [False, True])
def test_version_environment_does_not_join_or_modify_a_parent_uv_project(
    tmp_path, monkeypatch, no_config
):
    monkeypatch.setenv("UV_PYTHON", sys.executable)
    if no_config:
        monkeypatch.setenv("UV_NO_CONFIG", "1")
    else:
        monkeypatch.delenv("UV_NO_CONFIG", raising=False)
    bench = module()
    parent = tmp_path / "checkout"
    parent.mkdir()
    manifest = '[project]\nname="unrelated-parent"\nversion="0.1.0"\nrequires-python=">=3.13"\n'
    (parent / "pyproject.toml").write_text(manifest)
    env = {
        "id": "python-reference",
        "backend": "reference",
        "requirements": {"rdflib": "==7.6.0", "owlrl": "==7.6.2", "pyshacl": "==0.40.1"},
    }
    executable, installed = bench.setup(env, parent / "output/environments", None, "3.13")
    assert executable.exists()
    assert (parent / "pyproject.toml").read_text() == manifest
    assert not (parent / "uv.lock").exists()
    assert installed["packages"]["rdflib"]["version"] == "7.6.0"


def test_candidate_gate_uses_pinned_baselines_and_keeps_published_health_monitor():
    bench = module()
    root = bench.ROOT
    candidate = json.loads((root / "benchmarks/candidate-releases.json").read_text())
    environments = bench.validate_matrix(candidate)
    assert {env["id"] for env in environments} == {
        "python-reference",
        "turbo-historical",
        "candidate",
    }
    for env in environments:
        if env["id"] != "candidate":
            assert all(pin.startswith("==") for pin in env["requirements"].values())
    published = json.loads((root / "benchmarks/releases.json").read_text())
    bench.validate_matrix(published)
    assert (
        next(env for env in published["environments"] if env["id"] == "latest-published")["backend"]
        == "published"
    )
    assert [
        env for env in published["environments"] if env["id"] != "latest-published"
    ] == environments
    workflow = yaml.safe_load((root / ".github/workflows/shared-pipeline.yml").read_text())
    step = next(
        step
        for step in workflow["jobs"]["benchmark"]["steps"]
        if "benchmarks/releases.py" in step.get("run", "")
    )
    assert (
        step["env"]["BENCHMARK_MATRIX"]
        == "${{ github.event_name == 'schedule' && inputs.revision == '' && 'benchmarks/releases.json' || 'benchmarks/candidate-releases.json' }}"
    )
    assert '--matrix "$BENCHMARK_MATRIX"' in step["run"]
    assert "continue-on-error" not in step
