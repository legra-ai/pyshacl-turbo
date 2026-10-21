"""Unbridged public runner and graph-view contracts against pySHACL 0.40.1."""

import importlib

import pytest
from pyshacl.graph_abstraction import DataGraph as ReferenceDataGraph
from rdflib import Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

EX = Namespace("urn:runner:")


def wrapped(module, graph):
    return importlib.import_module(module + ".graph_abstraction").DataGraph.from_rdflib(graph)


@pytest.mark.parametrize("attribute", ["namespace_manager", "default_graph"])
def test_graph_wrapper_reference_properties_are_read_only(attribute):
    for module in ("pyshacl", "pyshacl_turbo"):
        graph = wrapped(module, Graph())
        original = getattr(graph, attribute)
        with pytest.raises(AttributeError, match="has no setter"):
            setattr(graph, attribute, None)
        assert getattr(graph, attribute) is original


def fixture(dataset=False):
    graph = Dataset(default_union=True) if dataset else Graph(identifier=EX.data)
    destination = graph.graph(EX.named) if dataset else graph
    destination.add((EX.a, RDF.type, EX.Person))
    destination.add((EX.a, EX.p, Literal(1)))
    shapes = Graph().parse(
        data="@prefix ex: <urn:runner:> .\n        @prefix sh: <http://www.w3.org/ns/shacl#> .\n        ex:S a sh:NodeShape; sh:targetClass ex:Person;\n          sh:property ex:P . ex:P sh:path ex:p; sh:minCount 2.",
        format="turtle",
    )
    return (graph, shapes)


@pytest.mark.parametrize("dataset", [False, True])
def test_graph_wrapper_is_live_and_preserves_contexts(dataset):
    expected_graph, _ = fixture(dataset)
    actual_graph, _ = fixture(dataset)
    expected = ReferenceDataGraph.from_rdflib(expected_graph)
    actual = wrapped("pyshacl_turbo", actual_graph)
    assert isinstance(actual, Dataset)
    assert actual.context_aware == expected.context_aware is True
    assert actual.identifier == expected.identifier
    assert type(actual.identifier) is type(expected.identifier)
    assert actual.is_multigraph() == expected.is_multigraph() == dataset
    assert actual.impl is actual_graph
    assert set(actual) == set(expected)
    assert len(actual) == len(expected)
    assert set(actual.objects(EX.a, EX.p)) == {Literal(1)}
    assert set(actual.subjects(EX.p, [Literal(1)])) == {EX.a}
    assert set(actual.objects([EX.a], EX.p)) == {Literal(1)}
    for facade, source in ((expected, expected_graph), (actual, actual_graph)):
        assert facade.add((EX.a, EX.added, Literal(True))) is source
        assert (EX.a, EX.added, Literal(True)) in facade
        facade.remove((EX.a, EX.added, None))
        facade.bind("ex", EX)
        assert dict(facade.namespaces())["ex"] == URIRef(EX)
        assert facade.default_graph is (source.default_graph if dataset else source)
    if dataset:
        assert set(actual.quads()) == set(expected.quads())
        locked = actual.with_locked_context(EX.named)
        assert set(locked) == set(expected.with_locked_context(EX.named))
        locked.add((EX.b, EX.p, Literal(2)))
        assert (EX.b, EX.p, Literal(2)) in actual_graph.graph(EX.named)
        assert (EX.b, EX.p, Literal(2)) not in actual_graph.default_graph
    else:
        assert actual.get_context(EX.other) is actual_graph
        with pytest.raises(ValueError, match="non-dataset"):
            actual.with_locked_context(EX.other)
    clone = actual.clone()
    assert set(clone) == set(actual)
    clone.add((EX.independent, EX.p, Literal(3)))
    assert (EX.independent, EX.p, Literal(3)) not in actual


def test_native_store_graph_cannot_bypass_guard_inside_datagraph():
    from pyshacl_turbo.graph_abstraction import DataGraph
    from pyshacl_turbo.rdf import input_graph, merge_graph

    class NativeStoreView(Graph):
        _turbo_native_graph = True

    data = DataGraph.from_rdflib_graph(Graph())
    data.impl = NativeStoreView()
    with pytest.raises(NotImplementedError, match="native Store"):
        input_graph(data)
    with pytest.raises(NotImplementedError, match="native Store"):
        merge_graph(data, Graph())
    with pytest.raises(NotImplementedError, match="native Store"):
        merge_graph(Graph(), data)


def test_datagraph_clone_and_factory_cannot_hide_native_backing():
    from pyshacl_turbo.graph_abstraction import DataGraph

    class NativeStoreView(Graph):
        _turbo_native_graph = True

    data = DataGraph.from_rdflib_graph(Graph())
    data.impl = NativeStoreView()
    with pytest.raises(NotImplementedError, match="native Store"):
        data.clone()
    with pytest.raises(NotImplementedError, match="native Store"):
        DataGraph.from_rdflib(data)
