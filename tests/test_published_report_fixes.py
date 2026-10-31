"""The selected published native owner supplies the original report wording."""

import pyshacl
import pyshacl_turbo
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, SH, XSD


def shape():
    graph = Graph()
    node = URIRef("urn:S")
    graph.add((node, RDF.type, SH.PropertyShape))
    graph.add((node, SH.targetNode, URIRef("urn:s")))
    graph.add((node, SH.path, URIRef("urn:p")))
    return graph, node


@pytest.mark.parametrize("message", ["true", "false"])
def test_published_owner_formats_boolean_messages_as_original_values(message):
    shapes, node = shape()
    shapes.add((node, SH.minCount, Literal("1", datatype=XSD.integer)))
    shapes.add((node, SH.message, Literal(message, datatype=XSD.boolean)))
    original = pyshacl.validate(Graph(), shacl_graph=shapes)
    actual = pyshacl_turbo.validate(Graph(), shacl_graph=shapes)
    assert actual[0] is original[0] is False
    assert actual[2] == original[2]
    assert isomorphic(actual[1], original[1])


def test_published_owner_preserves_original_unique_language_message():
    shapes, node = shape()
    shapes.add((node, SH.uniqueLang, Literal("true", datatype=XSD.boolean)))
    data = Graph()
    for word in ("first", "second"):
        data.add((URIRef("urn:s"), URIRef("urn:p"), Literal(word, lang="en")))
    original = pyshacl.validate(data, shacl_graph=shapes)
    actual = pyshacl_turbo.validate(data, shacl_graph=shapes)
    assert actual[0] is original[0] is False
    assert actual[2] == original[2]
    assert isomorphic(actual[1], original[1])
