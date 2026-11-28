"""The drop-in ``pyshacl`` commands match pySHACL's arguments and exit codes (ADR 0049)."""

from concurrent.futures import ThreadPoolExecutor

import pytest
from cli_parity import CASES, CliCase, Command, Outcome, write_files
from divergence_ledger import Ledger, Suite


@pytest.fixture(scope="module")
def outcomes(tmp_path_factory):
    directory = tmp_path_factory.mktemp("cli-parity")
    write_files(directory)

    def measure(case: CliCase):
        return case, case.reference(directory), *case.drop_in(directory)

    # bounded: the fixed case table above, not a graph relation.
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(measure, CASES))


def test_case_ids_are_unique_and_cover_both_commands():
    assert len({case.case_id for case in CASES}) == len(CASES)
    assert {case.command for case in CASES} == set(Command)


def test_module_and_installed_script_agree(outcomes):
    for case, _, module, script in outcomes:
        assert module == script, case.case_id


def test_every_cli_difference_is_in_the_ledger(outcomes):
    differing = [case.case_id for case, reference, module, _ in outcomes if module != reference]
    Ledger.load().reconcile(Suite.PYSHACL_CLI, differing)


def test_representative_exit_codes(outcomes):
    observed = {case.case_id: module for case, _, module, _ in outcomes}
    assert observed["validate/conforms"] == Outcome(0, True)
    assert observed["validate/violation"] == Outcome(1, False)
    assert observed["validate/unknown-option"].code == 2
    assert observed["validate/server-option"] == Outcome(1, None)
    assert observed["rules/expand"].code == 0


def test_outcome_reads_conformance_from_the_report_text():
    assert Outcome.of(0, "Conforms: True") == Outcome(0, True)
    assert Outcome.of(1, "Conforms: False") == Outcome(1, False)
    assert Outcome.of(2, "") == Outcome(2, None)
