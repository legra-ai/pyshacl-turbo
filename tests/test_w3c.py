"""Execute every Core case; W3C-expectation divergences come from the ledger only."""

import pyshacl_turbo as turbo
import pytest
from divergence_ledger import Baseline, Ledger, Suite
from suite_harness import cases, compare

EXPECTED = Ledger.load().select(Suite.W3C_SHACL10, Baseline.W3C_EXPECTATION)


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(
            case,
            id=case.id,
            marks=pytest.mark.xfail(
                strict=True, reason=f"{EXPECTED[case.id].adr.path}: {EXPECTED[case.id].reason}"
            ),
        )
        if case.id in EXPECTED
        else pytest.param(case, id=case.id)
        for case in cases("core")
    ],
)
def test_w3c_core(case):
    compare(case, turbo.validate)


def test_every_w3c_expectation_entry_names_a_core_case():
    assert set(EXPECTED) <= {case.id for case in cases("core")}
