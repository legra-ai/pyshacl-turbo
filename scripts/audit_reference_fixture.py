"""Run the corrected issue-70 test with both engines and compare full reports."""

import argparse
import hashlib
import importlib.util
import json
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from urllib.request import urlopen

import pyshacl
import pyshacl_turbo as turbo
from rdflib.compare import isomorphic
from rdflib.namespace import SH

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "vendor/pyshacl/test/issues/bad_test_070.py"
SHAPES = (
    "https://raw.githubusercontent.com/rapw3k/DEMETER/"
    "94762b9b0645f3b97dee675b15ee6278145a818b/models/SHACL/demeterAgriProfile-SHACL.ttl"
)
SHAPES_SHA256 = "ac57e99d7da5c9e87651cd424fd41f9db78659084dc8720d252d7c7f28906610"


def run_test(module, engine):
    calls = []

    def validate(*args, **kwargs):
        result = engine.validate(*args, **kwargs)
        calls.append(result)
        return result

    module.validate = validate
    module.test_070()
    return calls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/reference-fixture-audit.json")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("upstream_bad_test_070", TEST)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with urlopen(SHAPES, timeout=30) as response:
        shapes = response.read()
    if hashlib.sha256(shapes).hexdigest() != SHAPES_SHA256:
        raise RuntimeError("Pinned remote shapes checksum changed")
    # Run the actual corrected test against identical, checksum-verified shapes.
    module.shacl_url = shapes
    reports, corrected_reports, outputs = [], [], {}
    for name, engine in (("pyshacl", pyshacl), ("turbo", turbo)):
        (conforms, report, _), (corrected_conforms, corrected_report, _) = run_test(module, engine)
        reports.append(report)
        corrected_reports.append(corrected_report)
        rows = []
        for result in report.objects(None, SH.result):
            rows.append(sorted((str(p), str(o)) for p, o in report.predicate_objects(result)))
        outputs[name] = {
            "test_status": "passed",
            "conforms": conforms,
            "results": sorted(rows),
            "with_subclass_conforms": corrected_conforms,
        }
    agrees = isomorphic(*reports)
    corrected_agrees = isomorphic(*corrected_reports)
    output = {
        "date": datetime.now(UTC).isoformat(),
        "pyshacl": version("pyshacl"),
        "rdflib": version("rdflib"),
        "case": "test/issues/bad_test_070.py::test_070",
        "test_sha256": hashlib.sha256(TEST.read_bytes()).hexdigest(),
        "shapes_url": SHAPES,
        "shapes_sha256": SHAPES_SHA256,
        "report_graphs_isomorphic": agrees,
        "with_subclass_report_graphs_isomorphic": corrected_agrees,
        "engines": outputs,
        "corrected_test_status": "passed",
        "local_correction": "vendor/pyshacl-issue-70.patch",
        "reason": "The original data lacks the required geo:Geometry class. Both engines reject it with the same violation, then accept it when the missing sf:Point subclass relationship is supplied.",
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    if not agrees or not corrected_agrees:
        raise AssertionError("The engines returned different reports for the corrected test")
    print(
        "Both engines pass the corrected test: invalid data is rejected, the subclass addition "
        "makes it conform, and full reports agree in both cases."
    )


if __name__ == "__main__":
    main()
