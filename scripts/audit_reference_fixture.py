"""Compare both engines on the same immutable shapes for upstream bad_test_070.

This audit does not change the strict upstream test result or its denominator.
"""

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
from rdflib import Graph
from rdflib.compare import isomorphic
from rdflib.namespace import SH

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "vendor/pyshacl/test/issues/bad_test_070.py"
SHAPES = (
    "https://raw.githubusercontent.com/rapw3k/DEMETER/"
    "94762b9b0645f3b97dee675b15ee6278145a818b/models/SHACL/demeterAgriProfile-SHACL.ttl"
)
SHAPES_SHA256 = "ac57e99d7da5c9e87651cd424fd41f9db78659084dc8720d252d7c7f28906610"


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
    reports, outputs = [], {}
    for name, engine in (("pyshacl", pyshacl), ("turbo", turbo)):
        data = Graph().parse(data=module.data_text, format="turtle")
        conforms, report, _ = engine.validate(
            data, shacl_graph=shapes, shacl_graph_format="turtle", advanced=True
        )
        reports.append(report)
        rows = []
        for result in report.objects(None, SH.result):
            rows.append(sorted((str(p), str(o)) for p, o in report.predicate_objects(result)))
        outputs[name] = {"conforms": conforms, "results": sorted(rows)}
    agrees = isomorphic(*reports)
    output = {
        "date": datetime.now(UTC).isoformat(),
        "pyshacl": version("pyshacl"),
        "rdflib": version("rdflib"),
        "case": "test/issues/bad_test_070.py::test_070",
        "test_sha256": hashlib.sha256(TEST.read_bytes()).hexdigest(),
        "shapes_url": SHAPES,
        "shapes_sha256": SHAPES_SHA256,
        "report_graphs_isomorphic": agrees,
        "engines": outputs,
        "strict_upstream_status": "failed",
        "reason": "The test asserts conformance, but its geometry node lacks the required geo:Geometry class. Both engines report the same violation.",
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    if not agrees or any(result["conforms"] for result in outputs.values()):
        raise AssertionError("The documented reference failure no longer matches both engines")
    print(
        "Both engines reject the fixture with isomorphic reports; the upstream assertion remains failed."
    )


if __name__ == "__main__":
    main()
