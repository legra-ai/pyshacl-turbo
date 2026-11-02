"""Keep actual original Boolean assessments through ordinary execution."""

from xml.dom import Node

import pyshacl
import pyshacl_turbo as turbo
import pytest
import rdflib
from rdflib import Graph
from rdflib.namespace import SH


def metadata(value):
    cache = value.value
    payload = (
        tuple(child.toxml() for child in cache.childNodes)
        if isinstance(cache, Node)
        else repr(cache)
    )
    return str(value), value.datatype, value.language, type(cache), payload, value.ill_typed


@pytest.mark.parametrize("document", [False])
def test_invalid_boolean_assessment_survives_normalized_public_input(monkeypatch, document):
    monkeypatch.setattr(rdflib, "NORMALIZE_LITERALS", True)
    lexical = '<urn:s> <urn:p> "none"^^<http://www.w3.org/2001/XMLSchema#boolean> .'
    shapes = Graph().parse(
        data="""@prefix sh:<http://www.w3.org/ns/shacl#>.
        @prefix xsd:<http://www.w3.org/2001/XMLSchema#>.
        <urn:S> sh:targetNode <urn:s>; sh:path <urn:p>; sh:datatype xsd:boolean.""",
        format="turtle",
    )
    data = lexical if document else Graph().parse(data=lexical, format="turtle")
    before = None if document else [metadata(value) for value in data.objects()]
    expected = pyshacl.validate(data, shacl_graph=shapes, data_graph_format="turtle")
    assert expected[0] is False
    original = next(expected[1].objects(None, SH.value))
    assert str(original) == "false"
    assert original.ill_typed is True and original.value is False
    actual = turbo.validate(data, shacl_graph=shapes, data_graph_format="turtle")
    assert actual[0] is False, (
        expected[1].serialize(format="turtle"),
        actual[1].serialize(format="turtle"),
        expected[2],
        actual[2],
    )
    assert [metadata(value) for value in actual[1].objects(None, SH.value)] == [metadata(original)]
    if not document:
        assert [metadata(value) for value in data.objects()] == before


@pytest.mark.parametrize(
    "assessment,word",
    [
        ("valid", False),
        ("valid", True),
        ("invalid", False),
        ("unassessed", False),
        ("unassessed", True),
    ],
)
def test_canonical_boolean_value_metadata_matches_original(assessment, word):
    from rdflib import Literal, URIRef
    from rdflib.namespace import XSD

    value = (
        Literal(word)
        if assessment == "unassessed"
        else Literal(str(word).lower() if assessment == "valid" else "none", datatype=XSD.boolean)
    )
    data = Graph()
    data.add((URIRef("urn:s"), URIRef("urn:p"), value))
    shape = Graph().parse(
        data="""@prefix sh:<http://www.w3.org/ns/shacl#>.
        <urn:S> sh:targetNode <urn:s>; sh:path <urn:p>; sh:nodeKind sh:IRI.""",
        format="turtle",
    )
    before = [metadata(item) for item in data.objects()]
    expected = pyshacl.validate(data, shacl_graph=shape)
    actual = turbo.validate(data, shacl_graph=shape)
    assert actual[0] is expected[0] is False
    assert [metadata(item) for item in actual[1].objects(None, SH.value)] == [
        metadata(item) for item in expected[1].objects(None, SH.value)
    ]
    assert len(actual[1]) == len(expected[1]) == 11
    assert [metadata(item) for item in data.objects()] == before


@pytest.mark.parametrize("bad_first", [False, True])
def test_rdf_equal_boolean_insertion_order_retains_selected_assessment(bad_first):
    from rdflib import Literal, URIRef
    from rdflib.namespace import XSD

    good = Literal("false", datatype=XSD.boolean, normalize=False)
    bad = Literal("none", datatype=XSD.boolean, normalize=True)
    data = Graph()
    for item in (bad, good) if bad_first else (good, bad):
        data.add((URIRef("urn:s"), URIRef("urn:p"), item))
    shape = Graph().parse(
        data="""@prefix sh:<http://www.w3.org/ns/shacl#>.
        @prefix xsd:<http://www.w3.org/2001/XMLSchema#>.
        <urn:S> sh:targetNode <urn:s>; sh:path <urn:p>; sh:datatype xsd:boolean.""",
        format="turtle",
    )
    expected = pyshacl.validate(data, shacl_graph=shape)
    actual = turbo.validate(data, shacl_graph=shape)
    assert actual[0] is expected[0] is (not bad_first)
    assert len(actual[1]) == len(expected[1])
    assert [metadata(item) for item in actual[1].objects(None, SH.value)] == [
        metadata(item) for item in expected[1].objects(None, SH.value)
    ]


@pytest.mark.parametrize("bad_first", [False, True])
@pytest.mark.parametrize("selected", [False, True])
def test_shared_contexts_use_actual_selected_sp_authority(bad_first, selected):
    from rdflib import Dataset, Literal, URIRef
    from rdflib.namespace import XSD

    owner = Dataset(default_union=True)
    a, b = owner.graph(URIRef("urn:a")), owner.graph(URIRef("urn:b"))
    bad = Literal("none", datatype=XSD.boolean, normalize=True)
    good = Literal("false", datatype=XSD.boolean, normalize=False)
    for graph, value in ((a, bad), (b, good)) if bad_first else ((b, good), (a, bad)):
        graph.add((URIRef("urn:s"), URIRef("urn:p"), value))
    data = a if selected else owner
    shape = Graph().parse(
        data="""@prefix sh:<http://www.w3.org/ns/shacl#>.
        @prefix xsd:<http://www.w3.org/2001/XMLSchema#>.
        <urn:S> sh:targetNode <urn:s>; sh:path <urn:p>; sh:datatype xsd:boolean.""",
        format="turtle",
    )
    before = [(str(s), str(p), metadata(o), str(g)) for s, p, o, g in owner.quads()]
    expected = pyshacl.validate(data, shacl_graph=shape)
    actual = turbo.validate(data, shacl_graph=shape)
    assert actual[0] is expected[0]
    assert len(actual[1]) == len(expected[1])
    assert [metadata(item) for item in actual[1].objects(None, SH.value)] == [
        metadata(item) for item in expected[1].objects(None, SH.value)
    ]
    assert [(str(s), str(p), metadata(o), str(g)) for s, p, o, g in owner.quads()] == before


def test_sp_callback_error_keeps_actual_exception_identity():
    from rdflib import Literal, URIRef

    failure = LookupError("selected Boolean callback failed", 17)

    class Failing(Graph):
        def __iter__(self):
            return iter(((URIRef("urn:s"), URIRef("urn:p"), Literal(False)),))

        def triples(self, pattern):
            raise failure

    shape = Graph().parse(
        data="""@prefix sh:<http://www.w3.org/ns/shacl#>.
        <urn:S> sh:targetNode <urn:s>; sh:path <urn:p>; sh:nodeKind sh:IRI.""",
        format="turtle",
    )
    with pytest.raises(LookupError) as observed:
        turbo.validate(Failing(), shacl_graph=shape)
    assert observed.value is failure
    assert observed.value.args == ("selected Boolean callback failed", 17)
