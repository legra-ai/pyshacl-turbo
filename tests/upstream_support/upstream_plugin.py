import json
import os
from collections import Counter
from pathlib import Path

import pytest
from case_ids import portable_id
from redirect import configure_item, install

ROWS = {}
COLLECTION_ERRORS = []
ROOT = Path(__file__).resolve().parents[2]
CORRECTIONS = {"test/issues/bad_test_070.py::test_070": "vendor/pyshacl-issue-70.patch"}


def pytest_configure(config):
    from process_launch import install as install_process_launcher

    install_process_launcher()
    if os.environ.get("PYSHACL_TURBO_TEST_REDIRECT") == "1":
        install()


def pytest_collection_modifyitems(items):
    from native_equivalents import PORTS

    for item in items:
        ROWS[item.nodeid] = {
            "id": portable_id(item.nodeid, ROOT),
            "status": "not_run",
            "origin": "vendored",
        }
        if correction := CORRECTIONS.get(ROWS[item.nodeid]["id"]):
            ROWS[item.nodeid].update(local_correction=correction, origin="locally-corrected")
        if os.environ.get("PYSHACL_TURBO_TEST_REDIRECT") == "1" and item.nodeid in PORTS:
            port = PORTS[item.nodeid]
            module = item.module
            item.obj = lambda port=port, module=module: port(module)
            ROWS[item.nodeid].update(native_equivalent=port.__name__, origin="first-party")


def pytest_runtest_setup(item):
    configure_item(item, redirect_cli=os.environ.get("PYSHACL_TURBO_TEST_REDIRECT") == "1")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    row = ROWS[item.nodeid]
    if report.failed:
        row.update(status="failed", reason=str(report.longrepr))
    elif report.skipped:
        row.update(status="skipped", reason=str(report.longrepr))
    elif report.when == "call" and row["status"] == "not_run":
        row["status"] = "passed"


def pytest_collectreport(report):
    if report.failed:
        COLLECTION_ERRORS.append(
            {"id": portable_id(report.nodeid, ROOT), "reason": str(report.longrepr)}
        )


def origin_summary(rows):
    """Count outcomes per origin so corrected and first-party cases stay separate."""
    result = {}
    for row in rows:
        counts = result.setdefault(row["origin"], {})
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {origin: dict(sorted(counts.items())) for origin, counts in sorted(result.items())}


def pytest_sessionfinish(session, exitstatus):
    path = Path(os.environ["PYSHACL_TURBO_UPSTREAM_REPORT"])
    rows = list(ROWS.values())
    path.write_text(
        json.dumps(
            {
                "reference": "pySHACL 0.40.1",
                "engine": "turbo" if os.environ.get("PYSHACL_TURBO_TEST_REDIRECT") else "reference",
                "excluded": ["SHACL-JS"],
                "summary": dict(Counter(row["status"] for row in rows)),
                "origin_summary": origin_summary(rows),
                "collection_errors": COLLECTION_ERRORS,
                "cases": rows,
                "exit_status": exitstatus,
            },
            indent=2,
        )
        + "\n"
    )
