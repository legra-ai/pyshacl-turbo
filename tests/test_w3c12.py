"""Grade every pinned W3C SHACL 1.2 case for Turbo and plain pySHACL (ADR 0047)."""

import hashlib
import json
import logging
import warnings
from pathlib import Path

import pytest
from divergence_ledger import Ledger, Origin, Suite
from w3c_grading import (
    W3C_SHACL12,
    CaseType,
    NotRunReason,
    Outcome,
    Relation,
    SuiteTally,
    measure,
)

TESTS = Path(__file__).resolve().parent
# Discovered totals per manifest entry type at the pinned revision.
TOTALS = {
    CaseType.EVAL_NODE_EXPR: 276,
    CaseType.INFER: 41,
    CaseType.SRL_EVAL: 76,
    CaseType.SRL_NEGATIVE_STRATIFICATION: 10,
    CaseType.SRL_NEGATIVE_SYNTAX: 66,
    CaseType.SRL_NEGATIVE_WELL_FORMEDNESS: 19,
    CaseType.SRL_POSITIVE_STRATIFICATION: 11,
    CaseType.SRL_POSITIVE_SYNTAX: 146,
    CaseType.SRL_POSITIVE_WELL_FORMEDNESS: 14,
    CaseType.VALIDATE: 274,
}
NOT_RUN = {
    NotRunReason.NODE_EXPRESSIONS: 276,
    NotRunReason.RULE_INFERENCE: 41,
    NotRunReason.SPARQL_RL: 342,
    NotRunReason.RDF12_SYNTAX: 11,
}


@pytest.fixture(scope="module")
def results():
    logging.disable(logging.CRITICAL)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return list(measure(W3C_SHACL12))
    finally:
        logging.disable(logging.NOTSET)


def test_pinned_source_records_url_commit_date_license_and_checksums():
    source = json.loads((TESTS / "suite-sources.json").read_text(encoding="utf-8"))["w3c12"]
    assert source["repository"] == "w3c/data-shapes"
    assert source["url"] == (
        f"https://codeload.github.com/w3c/data-shapes/tar.gz/{source['revision']}"
    )
    assert source["committed_at"] == "2026-11-16T22:33:45Z"
    assert source["license"] == "W3C Software and Document License"
    assert "W3C Software and Document License" in (TESTS / "w3c12/LICENSE.md").read_text(
        encoding="utf-8"
    )
    sums = {}
    for line in (TESTS.parent / source["sha256sums"]).read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        sums[name] = digest
    assert sorted(sums) == source["files"]
    for name, digest in sums.items():
        assert hashlib.sha256((TESTS / "w3c12" / name).read_bytes()).hexdigest() == digest, name
    on_disk = {
        path.relative_to(TESTS / "w3c12").as_posix()
        for path in (TESTS / "w3c12").rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    assert on_disk == set(sums)


def test_discovered_totals_per_type_include_not_run_cases(results):
    tally = SuiteTally.of(results)
    assert tally.totals() == {kind.name: count for kind, count in TOTALS.items()}
    assert tally.not_run == {reason.name: count for reason, count in NOT_RUN.items()}
    for result in results:
        if result.case.not_run is not None:
            assert result.turbo.outcome is result.pyshacl.outcome is Outcome.NOT_RUN


def test_every_case_is_a_vendored_upstream_file(results):
    assert {result.case.origin for result in results} == {Origin.VENDORED}
    assert len({result.case.id for result in results}) == len(results)


def test_differences_from_pyshacl_match_the_ledger_exactly(results):
    differing = [r.case.id for r in results if r.relation is not Relation.PARITY]
    Ledger.load().reconcile(Suite.W3C_SHACL12, differing)
    ledger = Ledger.load().select(Suite.W3C_SHACL12)
    for result in results:
        if result.relation is Relation.BEYOND:
            assert ledger[result.case.id].kind == "intentional", result.case.id
        elif result.relation is not Relation.PARITY:
            assert ledger[result.case.id].kind == "gap", result.case.id


def test_committed_counts_match_this_measurement(results):
    committed = json.loads((TESTS.parent / "docs/conformance.json").read_text(encoding="utf-8"))
    assert committed[Suite.W3C_SHACL12.value] == SuiteTally.of(results).to_json()
