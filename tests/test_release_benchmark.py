"""Prevent version comparisons from inventing performance equivalence."""

import importlib.util
from pathlib import Path

import pytest


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
        "tests/upstream_support/process_launch.py",
    }
