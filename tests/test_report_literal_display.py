"""Report text uses pinned pySHACL literal descriptions, never RDF serialization."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import BNode, Graph, Literal, Namespace
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, SH, XSD

EX = Namespace("urn:example:")
ERROR = Namespace("http://www.daml.org/2002/03/agents/agent-ont#")
LITERALS = [
    Literal("plain"),
    Literal('say "hi"\\end'),
    Literal("line\nnext\tcol\rreturn"),
    Literal("français", lang="fr"),
    Literal("same", datatype=XSD.string),
    Literal("1", datatype=XSD.integer),
    Literal("+001", datatype=XSD.integer, normalize=False),
    Literal("true", datatype=XSD.boolean),
    Literal("1", datatype=XSD.boolean, normalize=False),
    Literal("01.20", datatype=XSD.decimal, normalize=False),
    Literal("opaque", datatype=EX.opaque),
]


@pytest.mark.parametrize("literal", LITERALS)
@pytest.mark.parametrize("nested", [False, True])
def test_complete_report_preserves_literal_descriptions(literal, nested):
    data = Graph()
    data.bind("ex", EX)
    shapes = Graph()
    shapes.bind("ex", EX)
    property_shape = BNode()
    shapes.add((EX.Shape, SH.targetNode, EX.s))
    shapes.add((EX.Shape, SH.property, property_shape))
    shapes.add((property_shape, SH.path, EX.required))
    shapes.add((property_shape, SH.minCount, Literal(1)))
    if nested:
        note = BNode()
        shapes.add((property_shape, EX.note, note))
        shapes.add((note, EX.value, literal))
    else:
        shapes.add((property_shape, EX.note, literal))
    expected = pyshacl.validate(data, shacl_graph=shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert actual[0] == expected[0] == False
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]


def test_complete_report_describes_inference_error_literal_without_reescaping():
    data = Graph()
    data.bind("err", ERROR)
    error = BNode()
    data.add((error, RDF.type, ERROR.ErrorMessage))
    data.add(
        (
            error,
            ERROR.error,
            Literal(
                "Lexical value of the literal 'bad' does not match its datatype "
                "(http://www.w3.org/2001/XMLSchema#integer)"
            ),
        )
    )
    shapes = Graph().parse(
        data="""@prefix sh:<http://www.w3.org/ns/shacl#>.
        <urn:S> sh:targetClass
        <http://www.daml.org/2002/03/agents/agent-ont#ErrorMessage>;
        sh:property [sh:path <urn:required>;sh:minCount 1].""",
        format="turtle",
    )
    expected = pyshacl.validate(data, shacl_graph=shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert actual[0] == expected[0] == False
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
