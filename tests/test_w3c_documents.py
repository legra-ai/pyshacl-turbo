"""Run every pinned W3C case through the public document-input API."""

import pyshacl_turbo as turbo
import pytest
from suite_harness import cases, compare


@pytest.mark.parametrize("case", cases(), ids=lambda case: case.id)
def test_w3c_document(case):
    compare(case, turbo.validate, documents=True)
