"""Preserve RDFLib literal identity through the entire native pipeline."""

import pyoxigraph as ox
import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Literal
from rdflib.namespace import XSD
from test_compatibility import EX, SH, compare, graph, reference_rules


@pytest.mark.parametrize("typed", [False, True])
@pytest.mark.parametrize("constraint", ['sh:in ("value")', 'sh:hasValue "value"', "sh:equals ex:q"])
def test_core_identity_distinguishes_plain_and_explicit_string(typed, constraint):
    data = graph('ex:s ex:q "value".')
    data.add((EX.s, EX.p, Literal("value", datatype=XSD.string if typed else None)))
    shapes = graph(f"""ex:S sh:targetNode ex:s; sh:path ex:p;
      {constraint}; sh:message "identity mismatch".""")
    result = compare(data, shapes)
    assert result[0] == (not typed)


@pytest.mark.parametrize("serialized", [False, True])
def test_cardinality_retains_both_string_forms(serialized):
    data = graph('ex:s ex:p "value", "value"^^xsd:string.')
    shapes = graph("""ex:S sh:targetNode ex:s; sh:path ex:p;
      sh:maxCount 1; sh:message "two terms".""")
    if serialized:
        data = data.serialize(format="turtle")
    assert not compare(data, shapes)[0]


def test_rules_copy_both_string_forms_without_changing_identity():
    data = graph('ex:s ex:p "value", "value"^^xsd:string.')
    shapes = graph("""ex:S sh:targetNode ex:s; sh:rule [a sh:SPARQLRule;
      sh:construct "CONSTRUCT { $this <https://example.com/copied> ?v } WHERE { $this <https://example.com/p> ?v }"] .""")
    actual = turbo.shacl_rules(data, shacl_graph=shapes)
    expected = reference_rules(data, shapes)
    assert set(actual) == set(expected)
    assert set(actual.objects(EX.s, EX.copied)) == {
        Literal("value"),
        Literal("value", datatype=XSD.string),
    }


def test_sparql_preserves_identity_but_compares_string_values():
    data = graph('ex:s ex:p "value", "value"^^xsd:string.')
    shapes = graph('''ex:S sh:targetNode ex:s; sh:message "distinct terms, equal values";
      sh:sparql [sh:select """SELECT $this WHERE {
        $this <https://example.com/p> ?a, ?b .
        FILTER(!sameTerm(?a, ?b) && ?a = ?b)
      }"""] .''')
    result = compare(data, shapes)
    assert not result[0]


@pytest.mark.parametrize("format", ["turtle", "xml", "json-ld", "nt"])
def test_document_loading_retains_explicit_string_datatype(format):
    expected = graph('ex:s ex:p "value", "value"^^xsd:string.')
    source = expected.serialize(format=format)
    assert set(turbo.load_from_source(source, rdf_format=format)) == set(expected)


@pytest.mark.parametrize("typed_shape", [False, True])
def test_store_string_identity_matches_reference_adapter(typed_shape):
    data = ox.Store()
    data.add(ox.Quad(ox.NamedNode(str(EX.s)), ox.NamedNode(str(EX.p)), ox.Literal("value")))
    shapes = graph('ex:S sh:targetNode ex:s; sh:path ex:p; sh:message "different".')
    shapes.add((EX.S, SH.hasValue, Literal("value", datatype=XSD.string if typed_shape else None)))
    expected = pyshacl.validate(data, shacl_graph=shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert actual[0] == expected[0]
