"""Constructed shapes preserve original format and context selection semantics."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import BNode, ConjunctiveGraph, Dataset, Graph, Namespace
from rdflib.compare import isomorphic
from rdflib_turbo import Graph as NativeGraph

SH = Namespace("http://www.w3.org/ns/shacl#")
EX = Namespace("urn:constructed-shapes:")


@pytest.fixture(scope="module")
def retained_sources():
    # Keep these bounded fixtures alive across reference calls and parametrizations.
    return []


def add_shape(graph, suffix):
    graph.add((EX["shape-" + suffix], SH.targetNode, EX["focus-" + suffix]))
    graph.add((EX["shape-" + suffix], SH["class"], EX.Required))
    return graph


@pytest.mark.parametrize("graph_type", (Graph, NativeGraph))
@pytest.mark.parametrize("rdf_format", (None, "turtle", "not-a-real-format"))
def test_constructed_shapes_ignore_document_format(
    graph_type, rdf_format, retained_sources, monkeypatch
):
    expected_shapes = add_shape(graph_type(), "one")
    actual_shapes = add_shape(graph_type(), "one")
    retained_sources.extend((expected_shapes, actual_shapes))
    expected = pyshacl.validate(Graph(), shacl_graph=expected_shapes, shacl_graph_format=rdf_format)

    def forbidden_traversal(*args, **kwargs):
        raise AssertionError("Native shapes must use the shared compiler")

    if graph_type is NativeGraph:
        monkeypatch.setattr(NativeGraph, "serialize", forbidden_traversal)
        monkeypatch.setattr(NativeGraph, "triples", forbidden_traversal)
    actual = turbo.validate(Graph(), shacl_graph=actual_shapes, shacl_graph_format=rdf_format)
    assert actual[0] is expected[0] is False
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
    assert set(actual[1].objects(None, SH.focusNode)) == {EX["focus-one"]}


def context_shapes(kind):
    if kind == "conjunctive":
        graph = ConjunctiveGraph(identifier=EX.default)
        default = graph.default_context
        named = graph.get_context(EX.named)
        blank = graph.get_context(BNode("scope"))
        graph.get_context(EX.empty)
        graph.get_context(BNode("empty-scope"))
    else:
        graph = Dataset(default_union=True)
        default = graph.default_graph
        named = graph.graph(EX.named)
        blank = graph.graph(BNode("scope"))
        graph.graph(EX.empty)
        graph.graph(BNode("empty-scope"))
    add_shape(default, "default")
    add_shape(named, "named")
    add_shape(blank, "blank")
    return graph


@pytest.mark.parametrize("kind", ("conjunctive", "dataset"))
def test_context_aware_shapes_match_complete_original_report(kind, retained_sources):
    expected_shapes = context_shapes(kind)
    actual_shapes = context_shapes(kind)
    retained_sources.extend((expected_shapes, actual_shapes))
    expected = pyshacl.validate(Graph(), shacl_graph=expected_shapes)
    actual = turbo.validate(Graph(), shacl_graph=actual_shapes)
    assert actual[0] is expected[0] is False
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
    assert set(actual[1].objects(None, SH.focusNode)) == {
        EX["focus-default"],
        EX["focus-named"],
        EX["focus-blank"],
    }
    actual_scopes = {
        (type(context.identifier), str(context.identifier)) for context in actual_shapes.contexts()
    }
    expected_scopes = {
        (type(context.identifier), str(context.identifier))
        for context in expected_shapes.contexts()
    }
    assert actual_scopes == expected_scopes
    assert (type(EX.named), str(EX.named)) in actual_scopes
    assert (BNode, "scope") in actual_scopes
    # A Memory ConjunctiveGraph does not declare empty contexts; Dataset does.
    assert ((type(EX.empty), str(EX.empty)) in actual_scopes) is (kind == "dataset")
    assert ((BNode, "empty-scope") in actual_scopes) is (kind == "dataset")
