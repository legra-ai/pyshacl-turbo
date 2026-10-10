"""CI gate for the complete strict suite plus the audited reference-fixture defect.

The report retains bad_test_070 as failed. Only that exact assertion failure is
permitted, and a separate immutable-fixture audit must prove both reports agree.
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DEFECT = "test/issues/bad_test_070.py::test_070"


def check_report(observed, baseline):
    for key in ("engine", "reference", "excluded"):
        if observed[key] != baseline[key]:
            raise RuntimeError(f"Changed upstream report contract: {key}")
    if observed["collection_errors"] or observed["exit_status"] != 1:
        raise RuntimeError("Strict upstream run did not finish with its one documented failure")
    rows = observed["cases"]
    actual_ids = [row["id"] for row in rows]
    expected_ids = {row["id"] for row in baseline["cases"]}
    if len(actual_ids) != len(set(actual_ids)) or set(actual_ids) != expected_ids:
        raise RuntimeError("The upstream case inventory changed or contains duplicates")
    ports = {row["id"]: row.get("native_equivalent") for row in baseline["cases"]}
    for row in rows:
        if row.get("native_equivalent") != ports[row["id"]]:
            raise RuntimeError(f"Undocumented native equivalent: {row['id']}")
        if row["id"] == REFERENCE_DEFECT:
            if row["status"] != "failed" or "assert False" not in row.get("reason", ""):
                raise RuntimeError("The reference-fixture defect no longer has its audited result")
        elif row["status"] != "passed":
            raise RuntimeError(f"Upstream regression: {row['id']} ({row['status']})")
    counts = dict(Counter(row["status"] for row in rows))
    if counts != observed["summary"] or counts.get("failed") != 1:
        raise RuntimeError("Upstream summary disagrees with its case-level results")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    baseline = json.loads((ROOT / "docs/upstream-coverage.json").read_text())
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_upstream.py"), "--output", str(args.output)],
        check=False,
    )
    if result.returncode != 1:
        raise RuntimeError(f"Unexpected upstream process exit status: {result.returncode}")
    observed = json.loads(args.output.read_text())
    check_report(observed, baseline)
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/audit_reference_fixture.py"),
            "--output",
            str(args.output.with_name("reference-fixture-audit.json")),
        ],
        check=True,
    )
    print(
        f"CI gate passed: {observed['summary']['passed']}/{len(observed['cases'])} strict passes; "
        "one audited reference assertion remains failed."
    )


if __name__ == "__main__":
    main()
