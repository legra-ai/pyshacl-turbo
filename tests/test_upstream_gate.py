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
        "exit_status": 0,
        "summary": {"passed": 2},
        "origin_summary": {"locally-corrected": {"passed": 1}, "vendored": {"passed": 1}},
        "cases": [
            {"id": "test/example.py::test_example", "status": "passed", "origin": "vendored"},
            {
                "id": "test/issues/bad_test_070.py::test_070",
                "status": "passed",
                "origin": "locally-corrected",
                "local_correction": "vendor/pyshacl-issue-70.patch",
            },
        ],
    }


def test_gate_requires_corrected_case_to_pass_and_retains_its_provenance(gate):
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
        lambda r: r["cases"][1].update(status="failed", reason="E   assert False"),
        lambda r: r["cases"][1].pop("local_correction"),
        lambda r: r["cases"][1].update(local_correction="undocumented.patch"),
        lambda r: r["collection_errors"].append({"id": "broken module"}),
        lambda r: r.update(exit_status=1),
        lambda r: r.update(exit_status=2),
        lambda r: r.update(summary={"passed": 1, "failed": 1}),
        lambda r: r["cases"][1].update(origin="vendored"),
        lambda r: r["cases"][0].update(origin="first-party"),
        lambda r: r["cases"][0].pop("origin"),
        lambda r: r.update(origin_summary={"vendored": {"passed": 2}}),
    ],
)
def test_gate_rejects_incomplete_or_changed_results(gate, change):
    observed = report()
    baseline = deepcopy(observed)
    change(observed)
    with pytest.raises(RuntimeError):
        gate.check_report(observed, baseline)


def test_corrected_and_first_party_cases_are_never_vendored_passes(gate):
    observed = report()
    observed["cases"].append(
        {
            "id": "test/native.py::test_port",
            "status": "passed",
            "origin": "first-party",
            "native_equivalent": "port",
        }
    )
    observed["summary"] = {"passed": 3}
    observed["origin_summary"] = gate.origin_summary(observed["cases"])
    gate.check_report(observed, deepcopy(observed))
    assert observed["origin_summary"]["vendored"] == {"passed": 1}


def test_reference_differences_reconcile_with_the_ledger(gate):
    from divergence_ledger import Baseline, Divergence, Kind, Ledger, LedgerMismatch, Suite

    observed = report()
    reference = deepcopy(observed)
    reference["cases"][0]["status"] = "failed"
    case = observed["cases"][0]["id"]
    entry = Divergence(
        Suite.PYSHACL_UPSTREAM,
        case,
        Kind.INTENTIONAL,
        Baseline.PYSHACL,
        "reference failure",
        Ledger.load().entries[0].adr,
    )
    gate.reconcile(observed, reference, Ledger((entry,)))
    with pytest.raises(LedgerMismatch) as unlisted:
        gate.reconcile(observed, reference, Ledger(()))
    assert (unlisted.value.unlisted, unlisted.value.stale) == ([case], [])
    with pytest.raises(LedgerMismatch) as stale:
        gate.reconcile(observed, deepcopy(observed), Ledger((entry,)))
    assert (stale.value.unlisted, stale.value.stale) == ([], [case])
    reference["cases"].pop()
    with pytest.raises(RuntimeError, match="inventory"):
        gate.reconcile(observed, reference, Ledger(()))
