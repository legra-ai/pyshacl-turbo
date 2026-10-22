"""Report lexical decoding preserves contexts and rejects malformed payloads."""

import pytest
from pyshacl_turbo.rdf import decode
from rdflib import BNode, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SH, XSD
from rdflib.plugins.parsers.ntriples import ParseError

EX = Namespace("urn:example:")
SOURCE = """_:result <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/shacl#ValidationResult> <urn:metadata>.
_:result <http://www.w3.org/ns/shacl#sourceShape> _:shape <urn:metadata>.
_:result <http://www.w3.org/ns/shacl#value> "+001"^^<http://www.w3.org/2001/XMLSchema#integer> <urn:metadata>.
_:shape <urn:example:note> "+001"^^<http://www.w3.org/2001/XMLSchema#integer> <urn:metadata>.
_:shape <urn:example:context> "second" <urn:other>.
"""


@pytest.mark.parametrize("preserve_ids", [False, True])
def test_report_nquads_retain_scopes_shared_blanks_and_direct_literal_identity(preserve_ids):
    report = decode(SOURCE, preserve_ids=preserve_ids, report=True, normalize=True)
    result = next(report.subjects(RDF.type, SH.ValidationResult))
    shape = report.value(result, SH.sourceShape)
    assert (result == BNode("result")) is preserve_ids
    assert (shape == BNode("shape")) is preserve_ids
    assert set(report.quads()) == {
        (result, RDF.type, SH.ValidationResult, URIRef("urn:metadata")),
        (result, SH.sourceShape, shape, URIRef("urn:metadata")),
        (
            result,
            SH.value,
            Literal("+001", datatype=XSD.integer, normalize=False),
            URIRef("urn:metadata"),
        ),
        (shape, EX.note, Literal(1), URIRef("urn:metadata")),
        (shape, EX.context, Literal("second"), URIRef("urn:other")),
    }


def test_report_parser_rejects_an_invalid_object_before_constructing_a_graph():
    with pytest.raises(ParseError):
        decode("<urn:s> <urn:p> invalid .", report=True)
