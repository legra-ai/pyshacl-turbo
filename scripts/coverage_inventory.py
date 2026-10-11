"""Record actual suite outcomes; unsupported and unexecuted are never passes."""

import ast
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

import pyshacl_turbo as turbo
from suite_harness import cases, compare


def w3c_results(*, documents=False):
    rows = []
    for case in cases():
        row = {"id": case.id}
        try:
            compare(case, turbo.validate, documents=documents)
        except NotImplementedError as error:
            row.update(status="unsupported", reason=str(error))
        except AssertionError as error:
            row.update(status="mismatch", reason=str(error))
        except Exception as error:  # noqa: BLE001 -- inventory must record each failure and continue
            row.update(status="error", reason=f"{type(error).__name__}: {error}")
        else:
            row["status"] = "pass"
        rows.append(row)
    return rows


def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/coverage.json"
    rows = w3c_results()
    documents = w3c_results(documents=True)
    upstream = []
    report_path = ROOT / "docs/upstream-coverage.json"
    executed = json.loads(report_path.read_text()) if report_path.exists() else None
    executed_cases = executed["cases"] if executed else []
    for path in sorted((ROOT / "vendor/pyshacl/test").rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
                "test_"
            ):
                prefix = f"{path.relative_to(ROOT / 'vendor/pyshacl')}::{node.name}"
                statuses = [
                    row["status"] for row in executed_cases if row["id"].split("[")[0] == prefix
                ]
                status = "not_run"
                if statuses:
                    status = next(
                        (s for s in ("failed", "not_run", "skipped") if s in statuses), "passed"
                    )
                elif "test_js" in path.parts or path.name == "test_108.py":
                    status = "excluded_js"
                upstream.append(
                    {
                        "file": str(path.relative_to(ROOT)),
                        "name": node.name,
                        "line": node.lineno,
                        "status": status,
                    }
                )
    result = {
        "sources": json.loads((ROOT / "tests/suite-sources.json").read_text()),
        "w3c_summary": dict(Counter(row["status"] for row in rows)),
        "w3c": rows,
        "w3c_document_summary": dict(Counter(row["status"] for row in documents)),
        "w3c_documents": documents,
        "upstream": upstream,
        "upstream_run": executed,
        "upstream_note": "Function inventory; execution counts use parametrized cases in upstream_run. Unexecuted and excluded cases are not passes.",
    }
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "w3c_graphs": result["w3c_summary"],
                "w3c_documents": result["w3c_document_summary"],
                "upstream_functions": len(upstream),
            }
        )
    )


if __name__ == "__main__":
    main()
