"""The divergence ledger is typed, exact in both directions and covers every suite."""

import importlib.util
import json
import logging
import warnings
from pathlib import Path

import pytest
from divergence_ledger import (
    AdrLink,
    Baseline,
    Divergence,
    Kind,
    Ledger,
    LedgerMismatch,
    Origin,
    Suite,
)
from w3c_grading import W3C_SHACL10, Relation, measure

ROOT = Path(__file__).resolve().parents[1]
ADR = "docs/adr/0047-conformance-divergence-ledger.md"
ROW = {
    "suite": "direct-contract",
    "case": "exports/example",
    "kind": "gap",
    "baseline": "pyshacl",
    "reason": "differs",
    "adr": ADR,
}


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"scripts/{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(tmp_path, body):
    path = tmp_path / "ledger.toml"
    path.write_text(body)
    return path


def test_the_committed_ledger_loads_into_typed_entries():
    ledger = Ledger.load()
    assert ledger.entries
    for entry in ledger.entries:
        assert isinstance(entry.suite, Suite) and isinstance(entry.kind, Kind)
        assert isinstance(entry.baseline, Baseline) and isinstance(entry.adr, AdrLink)
    assert set(ledger.counts()) == {suite.value for suite in Suite}


def test_entries_parse_with_optional_tracking():
    entry = Divergence.parse(
        ROW | {"tracking": "https://github.com/legra-ai/rdflib-turbo/pull/198"}
    )
    assert entry.key == (Suite.DIRECT_CONTRACT, Baseline.PYSHACL, "exports/example")
    assert Divergence.parse(ROW).tracking is None


@pytest.mark.parametrize(
    "row",
    [
        ROW | {"extra": "field"},
        {key: value for key, value in ROW.items() if key != "reason"},
        ROW | {"reason": ""},
        ROW | {"kind": "unknown"},
        ROW | {"suite": "elsewhere"},
        ROW | {"baseline": "nothing"},
        ROW | {"adr": "docs/adr/9999-missing.md"},
        ROW | {"adr": "README.md"},
        ROW | {"tracking": "https://example.org/issue/1"},
        ROW | {"tracking": 7},
    ],
)
def test_malformed_entries_are_rejected(row):
    with pytest.raises(ValueError):
        Divergence.parse(row)


def test_duplicate_entries_and_foreign_tables_are_rejected(tmp_path):
    table = "[[divergence]]\n" + "".join(f'{key} = "{value}"\n' for key, value in ROW.items())
    with pytest.raises(ValueError, match="Duplicate"):
        Ledger.load(write(tmp_path, table + table))
    with pytest.raises(ValueError, match="only"):
        Ledger.load(write(tmp_path, table + "[other]\nkey = 1\n"))
    assert len(Ledger.load(write(tmp_path, table)).entries) == 1


def test_reconciliation_rejects_unlisted_differences_and_stale_entries():
    ledger = Ledger((Divergence.parse(ROW),))
    ledger.reconcile(Suite.DIRECT_CONTRACT, ["exports/example"])
    with pytest.raises(LedgerMismatch) as unlisted:
        ledger.reconcile(Suite.DIRECT_CONTRACT, ["exports/example", "exports/new"])
    assert (unlisted.value.unlisted, unlisted.value.stale) == (["exports/new"], [])
    with pytest.raises(LedgerMismatch) as stale:
        ledger.reconcile(Suite.DIRECT_CONTRACT, [])
    assert (stale.value.unlisted, stale.value.stale) == ([], ["exports/example"])
    with pytest.raises(LedgerMismatch):
        ledger.reconcile(Suite.DIRECT_CONTRACT, ["exports/example"], Baseline.W3C_EXPECTATION)


def test_shacl10_differences_from_pyshacl_match_the_ledger():
    logging.disable(logging.CRITICAL)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            results = list(measure(W3C_SHACL10))
    finally:
        logging.disable(logging.NOTSET)
    assert len(results) == 120
    differing = [r.case.id for r in results if r.relation is not Relation.PARITY]
    Ledger.load().reconcile(Suite.W3C_SHACL10, differing)
    expectation = {r.case.id for r in results if r.turbo.outcome != "pass"}
    Ledger.load().reconcile(Suite.W3C_SHACL10, expectation, Baseline.W3C_EXPECTATION)


def test_committed_upstream_records_match_the_ledger_and_origins():
    gate = load_script("check_upstream")
    observed = json.loads((ROOT / "docs/upstream-coverage.json").read_text())
    reference = json.loads((ROOT / "docs/upstream-reference.json").read_text())
    gate.check_report(observed, observed)
    gate.reconcile(observed, reference, Ledger.load())
    corrected = [row for row in observed["cases"] if row["origin"] == Origin.LOCALLY_CORRECTED]
    assert [row["id"] for row in corrected] == ["test/issues/bad_test_070.py::test_070"]
    assert observed["origin_summary"][Origin.VENDORED] == {"passed": 400}
    for row in reference["cases"]:
        assert row["origin"] == gate.expected_origin(row)
    assert reference["origin_summary"] == gate.origin_summary(reference["cases"])


def test_committed_direct_contract_matches_the_ledger():
    contract = load_script("compare_contract")
    report = json.loads((ROOT / "docs/direct-contract.json").read_text())
    contract.reconcile_ledger(report["cases"], Ledger.load())
    with pytest.raises(RuntimeError, match="first-party"):
        contract.reconcile_ledger([{"id": "x", "status": "equal"}], Ledger.load())
