"""Selected draft list coverage, independent of reference-package parity."""

import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, SH

PREFIX = """@prefix sh:<http://www.w3.org/ns/shacl#>.
@prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>."""


@pytest.mark.parametrize(
    "constraint,body,conforms,component",
    [
        ("sh:minListLength 2", "(1 2)", True, "MinListLength"),
        ("sh:minListLength 3", "(1 2)", False, "MinListLength"),
        ("sh:maxListLength 1", "(1 2)", False, "MaxListLength"),
        ("sh:maxListLength 2", "(1 2)", True, "MaxListLength"),
        ("sh:uniqueMembers true", "(1 2 1)", False, "UniqueMembers"),
        ("sh:uniqueMembers false", "(1 2 1)", True, "UniqueMembers"),
        ("sh:memberShape <urn:M>", "(<urn:a> <urn:b>)", True, "MemberShape"),
        ("sh:memberShape <urn:M>", '(<urn:a> "bad")', False, "MemberShape"),
    ],
)
def test_list_constraints_preserve_list_head_reports(constraint, body, conforms, component):
    data = Graph().parse(data=f"{PREFIX} <urn:s> <urn:p> {body}.", format="turtle")
    head = data.value(URIRef("urn:s"), URIRef("urn:p"))
    shapes = Graph().parse(
        data=f"""{PREFIX}
        <urn:S> sh:targetNode <urn:s>; sh:property [sh:path <urn:p>; {constraint}].
        <urn:M> sh:nodeKind sh:IRI.""",
        format="turtle",
    )
    actual, report, _ = turbo.validate(data, shacl_graph=shapes)
    assert actual is conforms
    results = list(report.subjects(RDF.type, SH.ValidationResult))
    if not conforms:
        parent = report.value(
            predicate=SH.sourceConstraintComponent,
            object=URIRef(f"http://www.w3.org/ns/shacl#{component}ConstraintComponent"),
        )
        assert parent is not None
        assert report.value(parent, SH.value) == head
        assert report.value(parent, SH.resultPath) == URIRef("urn:p")
        assert not list(report.triples((head, RDF.first, None)))
        if component == "MemberShape":
            assert report.value(parent, SH.detail) is not None
    else:
        assert not results


def test_false_uniqueness_reports_malformed_lists_without_rendering_them():
    data = Graph().parse(
        data=f"{PREFIX} <urn:s> <urn:p> _:head. _:head rdf:first 1; rdf:rest _:head.",
        format="turtle",
    )
    shapes = Graph().parse(
        data=f"""{PREFIX}
        <urn:S> sh:targetNode <urn:s>;
          sh:property [sh:path <urn:p>; sh:uniqueMembers false].""",
        format="turtle",
    )
    conforms, report, text = turbo.validate(data, shacl_graph=shapes)
    assert not conforms
    assert list(report.objects(None, SH.value)) == [
        data.value(URIRef("urn:s"), URIRef("urn:p"))
    ]
    assert "UniqueMembersConstraintComponent" in text
