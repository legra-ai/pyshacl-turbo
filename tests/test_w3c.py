"""Execute every Core case; one documented reference-compatible divergence."""

import pyshacl_turbo as turbo
import pytest
from suite_harness import cases, compare


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(
            case,
            id=case.id,
            marks=pytest.mark.xfail(
                strict=True, reason="ADR 0007: pySHACL Graph input treats boolean lexical 1 as true"
            ),
        )
        if case.path.stem == "uniqueLang-002"
        else pytest.param(case, id=case.id)
        for case in cases("core")
    ],
)
def test_w3c_core(case):
    compare(case, turbo.validate)
