"""The CI gate must never hide missing cases, skips, or new failures."""

import importlib.util
from copy import deepcopy
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "check_upstream", Path(__file__).resolve().parents[1] / "scripts/check_upstream.py"
)


@pytest.fixture
def gate():
    module = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(module)
    return module


def report():
    return {
        "engine": "turbo",
        "reference": "pySHACL 0.40.1",
        "excluded": ["SHACL-JS"],
        "collection_errors": [],
        "exit_status": 1,
        "summary": {"passed": 1, "failed": 1},
        "cases": [
            {"id": "test/example.py::test_example", "status": "passed"},
            {
                "id": "test/issues/bad_test_070.py::test_070",
                "status": "failed",
                "reason": "E   assert False",
            },
        ],
    }


def test_gate_keeps_documented_reference_assertion_failed(gate):
    observed = report()
    original = deepcopy(observed)
    gate.check_report(observed, original)
    assert observed == original


@pytest.mark.parametrize(
    "change",
    [
        lambda r: r["cases"].pop(),
        lambda r: r["cases"].append(r["cases"][0]),
        lambda r: r["cases"][0].update(status="skipped"),
        lambda r: r["cases"][0].update(status="failed"),
        lambda r: r["cases"][0].update(id="test/different.py::test_case"),
        lambda r: r["cases"][0].update(native_equivalent="undocumented_substitute"),
        lambda r: r["cases"][1].update(reason="Network error"),
        lambda r: r["collection_errors"].append({"id": "broken module"}),
        lambda r: r.update(exit_status=2),
        lambda r: r.update(summary={"passed": 2}),
    ],
)
def test_gate_rejects_incomplete_or_changed_results(gate, change):
    observed = report()
    baseline = deepcopy(observed)
    change(observed)
    with pytest.raises(RuntimeError):
        gate.check_report(observed, baseline)
