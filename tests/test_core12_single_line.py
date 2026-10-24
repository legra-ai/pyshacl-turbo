"""Selected SHACL 1.2 draft coverage, independent of reference-package parity."""

import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SH


@pytest.mark.parametrize("enabled", [True, False])
@pytest.mark.parametrize("separator", ["\n", "\v", "\f", "\r", "\r\n"])
def test_single_line_preserves_python_literal_and_report_identity(enabled, separator):
    focus, predicate, shape = map(URIRef, ["urn:focus", "urn:label", "urn:shape"])
    value = Literal(f"left{separator}right", lang="en")
    data = Graph().add((focus, predicate, value))
    shapes = Graph().parse(
        data=f"""@prefix sh: <http://www.w3.org/ns/shacl#>.
        <{shape}> a sh:NodeShape; sh:targetNode <{focus}>;
          sh:property [ sh:path <{predicate}>; sh:singleLine {str(enabled).lower()} ].""",
        format="turtle",
    )
    conforms, report, _ = turbo.validate(data, shacl_graph=shapes)
    assert conforms is not enabled
    results = list(report.subjects(RDF.type, SH.ValidationResult))
    if enabled:
        assert len(results) == 1
        result = results[0]
        assert report.value(result, SH.focusNode) == focus
        assert report.value(result, SH.resultPath) == predicate
        assert report.value(result, SH.value) == value
        assert report.value(result, SH.sourceConstraintComponent) == URIRef(
            "http://www.w3.org/ns/shacl#SingleLineConstraintComponent"
        )
    else:
        assert not results
