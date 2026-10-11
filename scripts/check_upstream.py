"""Require every case in the locally corrected upstream suite to pass."""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_report(observed, baseline):
    for key in ("engine", "reference", "excluded"):
        if observed[key] != baseline[key]:
            raise RuntimeError(f"Changed upstream report contract: {key}")
    if observed["collection_errors"] or observed["exit_status"] != 0:
        raise RuntimeError("The corrected upstream suite did not finish successfully")
    rows = observed["cases"]
    actual_ids = [row["id"] for row in rows]
    expected_ids = {row["id"] for row in baseline["cases"]}
    if len(actual_ids) != len(set(actual_ids)) or set(actual_ids) != expected_ids:
        raise RuntimeError("The upstream case inventory changed or contains duplicates")
    expected = {row["id"]: row for row in baseline["cases"]}
    for row in rows:
        for key in ("native_equivalent", "local_correction"):
            if row.get(key) != expected[row["id"]].get(key):
                raise RuntimeError(f"Changed upstream case provenance: {row['id']} ({key})")
        if row["status"] != "passed":
            raise RuntimeError(f"Upstream regression: {row['id']} ({row['status']})")
    counts = dict(Counter(row["status"] for row in rows))
    if counts != observed["summary"]:
        raise RuntimeError("Upstream summary disagrees with its case-level results")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    baseline = json.loads((ROOT / "docs/upstream-coverage.json").read_text())
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_upstream.py"), "--output", str(args.output)],
        check=True,
    )
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
        f"CI gate passed: {observed['summary']['passed']}/{len(observed['cases'])} "
        "corrected-suite passes; documented fixture correction audited with both engines."
    )


if __name__ == "__main__":
    main()
