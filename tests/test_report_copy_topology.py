"""Complete report graphs follow reference root and descendant copy identity."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Namespace
from rdflib.compare import isomorphic
from rdflib.namespace import SH

EX = Namespace("urn:example:")
PREFIXES = """@prefix ex:<urn:example:>. @prefix sh:<http://www.w3.org/ns/shacl#>.
@prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>.\n"""
CASES = {
    "reused-item": (
        "_:head",
        """_:head rdf:first _:shared; rdf:rest _:tail.
        _:tail rdf:first _:shared; rdf:rest rdf:nil. _:shared ex:p "same".""",
    ),
    "reused-properties": ("_:shared;ex:other _:shared", '_:shared ex:p "same".'),
    "deep-collection": ("(" * 24 + '"deep"' + ")" * 24, ""),
    "generic-cycle": ("_:cycle", "_:cycle ex:back _:cycle."),
    "list-extra-predicates": (
        "_:head",
        '_:head rdf:first "first"; rdf:rest rdf:nil;ex:ignored "annotation".',
    ),
}


def inputs(case, *, two_results=False):
    note, extra = CASES[case]
    targets = "ex:s,ex:t" if two_results else "ex:s"
    data = Graph()
    data.bind("ex", EX)
    shapes = Graph().parse(
        data=PREFIXES
        + f"ex:S sh:targetNode {targets}; sh:property [sh:path ex:required;"
        + f"sh:minCount 1;ex:note {note}]."
        + extra,
        format="turtle",
    )
    return data, shapes


def reference_shapes(shapes):
    result = Graph()
    result += shapes
    for prefix, namespace in shapes.namespaces():
        result.bind(prefix, namespace)
    return result


@pytest.mark.parametrize("case", CASES)
def test_complete_report_graph_copies_each_descendant_occurrence(case):
    data, shapes = inputs(case)
    before = set(data), set(shapes), tuple(data.namespaces()), tuple(shapes.namespaces())
    original_shapes = reference_shapes(shapes)
    expected = pyshacl.validate(data, shacl_graph=original_shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert actual[0] == expected[0] == False
    assert isomorphic(actual[1], expected[1])
    assert (set(data), set(shapes), tuple(data.namespaces()), tuple(shapes.namespaces())) == (
        before[0],
        set(original_shapes),
        before[2],
        before[3],
    )


def test_direct_roots_keep_identity_and_are_cached_across_results():
    data, shapes = inputs("reused-properties", two_results=True)
    expected = pyshacl.validate(data, shacl_graph=reference_shapes(shapes))
    actual = turbo.validate(data, shacl_graph=shapes)
    shape_root = shapes.value(EX.S, SH.property)
    for report in (expected[1], actual[1]):
        results = list(report.objects(None, SH.result))
        assert len(results) == 2
        assert {report.value(result, SH.sourceShape) for result in results} == {shape_root}
        assert len(set(report.objects(shape_root, EX.note))) == 1
    assert isomorphic(actual[1], expected[1])
