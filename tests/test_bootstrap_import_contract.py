"""Imports and document preparation follow real public source boundaries."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import OWL, RDF, SH
from rdflib_turbo import Graph as NativeGraph
from rdflib_turbo import StoreDataset

EX = Namespace("urn:bootstrap-import:")


def triples(graph):
    result = Graph()
    for triple in graph.triples((None, None, None)):
        result.add(triple)
    return result


@pytest.mark.parametrize("operation", ("validate", "shacl_rules"))
@pytest.mark.parametrize("graph_type", (NativeGraph, StoreDataset))
def test_native_shape_import_rejection_precedes_bootstrap_writes(operation, graph_type):
    source = graph_type()
    source.add((EX.shape, SH.targetNode, EX.focus))
    source.add((EX.shape, SH["class"], EX.Required))
    before = set(source.triples((None, None, None)))
    namespaces = tuple(source.namespaces())
    data = Graph()
    with pytest.raises(NotImplementedError, match="Native shapes OWL imports"):
        getattr(turbo, operation)(data, shacl_graph=source, do_owl_imports=True)
    assert set(source.triples((None, None, None))) == before
    assert tuple(source.namespaces()) == namespaces
    assert not data


@pytest.mark.parametrize("operation", ("validate", "shacl_rules"))
def test_implicit_shapes_do_not_import_data_ontology(operation, tmp_path):
    imported = tmp_path / "shapes.ttl"
    imported.write_text(
        "@prefix sh: <http://www.w3.org/ns/shacl#> . "
        "@prefix ex: <urn:bootstrap-import:> . "
        "ex:shape sh:targetNode ex:focus; sh:class ex:Required; sh:rule ex:rule . "
        "ex:rule a sh:TripleRule; sh:subject sh:this; sh:predicate ex:derived; sh:object ex:value ."
    )
    original = Graph()
    actual = Graph()
    for graph in (original, actual):
        graph.add((EX.source, OWL.imports, URIRef(imported.as_uri())))
    before = set(actual)
    namespaces = tuple(actual.namespaces())
    expected = getattr(pyshacl, operation)(original, do_owl_imports=True, advanced=True)
    observed = getattr(turbo, operation)(actual, do_owl_imports=True, advanced=True)
    if operation == "validate":
        assert observed[0] is expected[0] is True
        assert isomorphic(observed[1], expected[1])
        assert observed[2] == expected[2]
    else:
        assert isomorphic(triples(observed), triples(expected))
        assert (EX.focus, EX.derived, EX.value) not in observed
    assert set(actual) == set(original) == before
    assert tuple(actual.namespaces()) == namespaces


@pytest.mark.parametrize("operation", ("validate", "shacl_rules"))
def test_implicit_document_preinference_keeps_full_original_result(operation):
    document = (
        b"@prefix sh: <http://www.w3.org/ns/shacl#> . "
        b"@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . "
        b"@prefix ex: <urn:bootstrap-import:> . "
        b"ex:focus a ex:C . ex:C rdfs:subClassOf ex:D . "
        b"ex:shape sh:targetNode ex:focus; sh:class ex:D; sh:rule ex:rule . "
        b"ex:rule a sh:TripleRule; sh:subject sh:this; sh:predicate ex:derived; sh:object ex:value ."
    )
    expected = getattr(pyshacl, operation)(
        document, data_graph_format="turtle", inference="rdfs", advanced=True
    )
    actual = getattr(turbo, operation)(
        document, data_graph_format="turtle", inference="rdfs", advanced=True
    )
    if operation == "validate":
        assert actual[0] is expected[0] is True
        assert isomorphic(actual[1], expected[1])
        assert actual[2] == expected[2]
    else:
        assert (EX.focus, RDF.type, EX.D) in actual
        assert (EX.focus, EX.derived, EX.value) in actual
        assert isomorphic(triples(actual), triples(expected))
