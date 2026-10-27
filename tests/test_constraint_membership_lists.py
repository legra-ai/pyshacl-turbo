"""Membership collections use RDFLib.items semantics, not path-list grammar."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import OWL, RDF, RDFS, SH, XSD
from rdflib_turbo import Graph as NativeGraph

EX = Namespace("urn:membership-list:")
SYSTEM = {
    (OWL.Class, RDFS.subClassOf, RDFS.Class),
    (OWL.DatatypeProperty, RDFS.subClassOf, RDF.Property),
}


def fixtures(kind, graph_type=Graph):
    data, shapes = Graph(), graph_type()
    for graph in (data, shapes):
        graph.bind("ex", EX)
    data.add((EX.focus, EX.p, EX.value))
    shapes.add((EX.shape, RDF.type, SH.PropertyShape))
    shapes.add((EX.shape, SH.targetNode, EX.focus))
    shapes.add((EX.shape, SH.path, EX.p))
    head = {
        "iri": EX.notList,
        "blank": BNode("not-list"),
        "literal": Literal("not-list"),
        "nil": RDF.nil,
        "described-nil": RDF.nil,
    }.get(kind, BNode("head"))
    shapes.add((EX.shape, SH["in"], head))
    if kind in ("valid", "first-only", "described-nil", "cycle"):
        shapes.add((head, RDF.first, EX.value))
    if kind == "valid":
        shapes.add((head, RDF.rest, RDF.nil))
    elif kind == "rest-only":
        shapes.add((head, RDF.rest, EX.tail))
        shapes.add((EX.tail, RDF.first, EX.value))
        shapes.add((EX.tail, RDF.rest, RDF.nil))
    elif kind == "cycle":
        shapes.add((head, RDF.rest, head))
    return data, shapes


def assert_report(actual, expected):
    assert actual[0] is expected[0]
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
    assert set(actual[1].objects(None, SH.resultMessage)) == set(
        expected[1].objects(None, SH.resultMessage)
    )


@pytest.mark.parametrize(
    "kind", ("iri", "blank", "literal", "nil", "valid", "first-only", "rest-only", "described-nil")
)
@pytest.mark.parametrize("graph_type", (Graph, NativeGraph))
def test_membership_heads_match_complete_original_reports(kind, graph_type, monkeypatch):
    original_data, original_shapes = fixtures(kind)
    data, shapes = fixtures(kind, graph_type)
    before_data, before_shapes = set(data), set(shapes)
    namespaces = dict(shapes.namespaces())
    expected = pyshacl.validate(original_data, shacl_graph=original_shapes)

    def forbid_traversal(*args, **kwargs):
        raise AssertionError("Native membership compilation must borrow its source")

    with monkeypatch.context() as patch:
        if graph_type is NativeGraph:
            patch.setattr(NativeGraph, "triples", forbid_traversal)
            patch.setattr(NativeGraph, "serialize", forbid_traversal)
        actual = turbo.validate(data, shacl_graph=shapes)
    assert_report(actual, expected)
    assert set(data) == set(original_data) == before_data
    assert set(shapes) == set(original_shapes) == before_shapes | SYSTEM
    assert dict(shapes.namespaces()) == namespaces


@pytest.mark.parametrize("graph_type", (Graph, NativeGraph))
def test_membership_cycles_keep_original_value_error_and_input_state(graph_type):
    original_data, original_shapes = fixtures("cycle")
    data, shapes = fixtures("cycle", graph_type)
    before_data, before_shapes = set(data), set(shapes)
    with pytest.raises(ValueError) as expected:
        pyshacl.validate(original_data, shacl_graph=original_shapes)
    with pytest.raises(ValueError) as actual:
        turbo.validate(data, shacl_graph=shapes)
    assert (
        str(actual.value) == str(expected.value) == "List contains a recursive rdf:rest reference"
    )
    assert set(data) == before_data
    assert set(shapes) == set(original_shapes) == before_shapes | SYSTEM


CURSORS = [
    URIRef(""),
    BNode(""),
    Literal(""),
    Literal("", lang="en"),
    Literal("false", datatype=XSD.boolean, normalize=False),
    Literal("invalid", datatype=XSD.boolean, normalize=False),
    Literal("0", datatype=XSD.integer, normalize=False),
    Literal("-0_0", datatype=XSD.integer, normalize=False),
    Literal("١", datatype=XSD.integer, normalize=False),
    Literal("٠", datatype=XSD.integer, normalize=False),
    Literal("0.00", datatype=XSD.decimal, normalize=False),
    Literal("NaN", datatype=XSD.decimal, normalize=False),
    Literal("0.0", datatype=XSD.double, normalize=False),
    Literal("NaN", datatype=XSD.double, normalize=False),
    Literal(" ", datatype=XSD.base64Binary, normalize=False),
    Literal("!", datatype=XSD.base64Binary, normalize=False),
    Literal("AA==", datatype=XSD.base64Binary, normalize=False),
    Literal("00", datatype=XSD.hexBinary, normalize=False),
    Literal("[]", datatype=RDF.JSON, normalize=False),
    Literal("", datatype=RDF.JSON, normalize=False),
    Literal("PT0S", datatype=XSD.duration, normalize=False),
    Literal("PT0.0000006S", datatype=XSD.duration, normalize=False),
]


@pytest.mark.parametrize("head", CURSORS, ids=lambda node: node.n3())
def test_stock_cursor_truthiness_is_not_sparql_ebv(head):
    original_data, original_shapes = fixtures("iri")
    data, shapes = fixtures("iri")
    for graph in (original_shapes, shapes):
        graph.set((EX.shape, SH["in"], head))
        graph.add((head, RDF.first, EX.value))
        graph.add((head, RDF.rest, RDF.nil))
    expected = pyshacl.validate(original_data, shacl_graph=original_shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert expected[0] is bool(head)
    assert_report(actual, expected)


@pytest.mark.parametrize("codepoint", (0x11BF0, 0x10D40, 0x1E5F1))
@pytest.mark.parametrize("datatype", (XSD.integer, XSD.decimal, XSD.double))
def test_membership_numeric_cursor_uses_host_unicode_digit_tables(codepoint, datatype):
    head = Literal(chr(codepoint), datatype=datatype, normalize=False)
    original_data, original_shapes = fixtures("iri")
    data, shapes = fixtures("iri")
    for graph in (original_shapes, shapes):
        graph.set((EX.shape, SH["in"], head))
        graph.add((head, RDF.first, EX.value))
        graph.add((head, RDF.rest, RDF.nil))
    expected = pyshacl.validate(original_data, shacl_graph=original_shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert expected[0] is bool(head)
    assert_report(actual, expected)


@pytest.mark.parametrize("datatype", (XSD.base64Binary, XSD.hexBinary))
@pytest.mark.parametrize("lexical", ("???", "***", " \t\n", "é"))
def test_binary_cursor_decoder_permissiveness_matches_complete_reports(datatype, lexical):
    head = Literal(lexical, datatype=datatype, normalize=False)
    original_data, original_shapes = fixtures("iri")
    data, shapes = fixtures("iri")
    for graph in (original_shapes, shapes):
        graph.set((EX.shape, SH["in"], head))
        graph.add((head, RDF.first, EX.value))
        graph.add((head, RDF.rest, RDF.nil))
    expected = pyshacl.validate(original_data, shacl_graph=original_shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert expected[0] is bool(head)
    assert_report(actual, expected)
