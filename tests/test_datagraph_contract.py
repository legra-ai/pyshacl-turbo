"""Unbridged public runner and graph-view contracts against pySHACL 0.40.1."""

import importlib

import pyshacl_turbo as turbo
import pytest
from pyshacl.graph_abstraction import DataGraph as ReferenceDataGraph
from rdflib import Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

EX = Namespace("urn:runner:")


@pytest.mark.parametrize("default_union", [False, True])
def test_dataset_clone_preserves_reference_union_policy(default_union):
    source = Dataset(default_union=default_union)
    source.graph(EX.named).add((EX.a, EX.p, Literal(1)))
    for module in ("pyshacl", "pyshacl_turbo"):
        clone = wrapped(module, source).clone()
        assert clone.default_union is default_union
        assert clone.impl.default_union is default_union
        assert set(clone.quads()) == set(source.quads())


def test_dataset_clone_keeps_nonstandard_default_graph_identifier():
    source = Dataset()
    source.default_graph = source.graph(EX.default)
    source.default_graph.add((EX.a, EX.p, Literal("default")))
    for module in ("pyshacl", "pyshacl_turbo"):
        clone = wrapped(module, source).clone()
        assert clone.default_graph.identifier == source.default_graph.identifier
        assert set(clone.quads()) == set(source.quads())


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


@pytest.mark.parametrize("module", ["pyshacl", "pyshacl_turbo"])
def test_datagraph_factory_invalid_source_and_direct_store_construction(module):
    abstraction = importlib.import_module(module + ".graph_abstraction")
    with pytest.raises(ValueError, match="Invalid rdflib source type"):
        abstraction.DataGraph.from_rdflib("not a graph")
    store = Graph().store
    actual = abstraction.DataGraph(store)
    assert actual.is_multigraph()
    dataset = Dataset(default_union=True)
    data = abstraction.DataGraph.from_rdflib_dataset(dataset)
    assert data.impl is dataset
    nested = abstraction.DataGraph.from_rdflib(data)
    assert nested is not data and nested.impl is data


def test_graph_access_methods_follow_reference_and_query_bindings():
    from rdflib.namespace import RDFS

    outputs = []
    for module in ("pyshacl", "pyshacl_turbo"):
        source, _ = fixture(True)
        source.graph(EX.named).add((EX.Person, RDFS.subClassOf, EX.Super))
        data = wrapped(module, source)
        data.bind("ex", EX)
        assert list(data.query("SELECT ?o WHERE { ?s ex:p ?o }", initBindings={"s": EX.a})) == [
            (Literal(1),)
        ]
        outputs.append(
            (
                set(data.predicate_objects(EX.a)),
                set(data.subject_objects(EX.p)),
                set(data.subject_predicates(Literal(1))),
                set(data.transitive_objects(EX.Person, RDFS.subClassOf)),
                set(data.transitive_subjects(RDFS.subClassOf, EX.Super)),
            )
        )
        assert set(data.contexts())
        data.default_union = False
        assert not source.default_union
        data.default_union = True
        assert source.default_union
        clone = data.clone(destination=Dataset(default_union=True))
        assert set(clone) == set(data)
        assert clone.impl is not source
    assert outputs[0] == outputs[1]


def test_non_dataset_wrapped_graph_does_not_leak_other_store_contexts():
    store = Dataset(default_union=True)
    graph = store.graph(EX.selected)
    graph.add((EX.a, EX.p, Literal(1)))
    store.graph(EX.other).add((EX.secret, EX.p, Literal(2)))
    data = wrapped("pyshacl_turbo", graph)
    from pyshacl_turbo.rdf import input_graph, load_from_source

    result = load_from_source(input_graph(data))
    assert set(result) == set(graph)
    assert (EX.secret, EX.p, Literal(2)) not in result
    assert set(data.graphs()) == {graph}


def test_clone_retains_bindings_and_locked_context_uses_its_own_store():
    source = Graph(identifier=EX.graph)
    source.bind("custom", EX)
    data = wrapped("pyshacl_turbo", source)
    clone = data.clone(identifier="custom-identifier")
    assert dict(clone.namespaces())["custom"] == URIRef(EX)
    assert clone.identifier == "custom-identifier"
    assert clone.store is clone.impl.store


def test_graph_factories_context_constructor_and_collection_methods():
    from pyshacl_turbo.graph_abstraction import DataGraph, RdfLibDataGraph
    from pyshacl_turbo.rdf import merge_graph

    source = Graph(identifier=EX.data)
    source.add((EX.list, RDF.first, Literal(1)))
    source.add((EX.list, RDF.rest, RDF.nil))
    data = DataGraph.from_rdflib_graph(source)
    assert list(data.items(EX.list)) == [Literal(1)]
    assert data.default_union is False
    assert len(list(data.quads((EX.list, None, None, None)))) == 2
    selected = RdfLibDataGraph(source.store, source, locked_context="urn:other")
    assert selected.locked_context is source
    dataset = Dataset(default_union=True)
    dataset.graph(EX.named).add((EX.a, EX.p, Literal(1)))
    locked = RdfLibDataGraph(dataset.store, dataset, locked_context=str(EX.named))
    assert locked.identifier == EX.named
    assert (EX.a, EX.p, Literal(1)) in locked
    data.register_custom_function(EX.double, lambda term: Literal(int(term) * 2))
    try:
        assert list(data.query("SELECT (<urn:runner:double>(2) AS ?answer) WHERE {}")) == [
            (Literal(4),)
        ]
    finally:
        data.unregister_custom_function(EX.double, None)
    target = DataGraph.from_rdflib_graph(Graph())
    merge_graph(target, data)
    assert set(target.triples((None, None, None))) == set(source)


@pytest.mark.parametrize(
    "operation", ["data-graph", "validate", "rules", "compile", "input", "merge"]
)
def test_native_store_graphs_fail_before_cross_runtime_copy(operation):
    from pyshacl_turbo.graph_abstraction import DataGraph
    from pyshacl_turbo.rdf import input_graph, merge_graph

    class NativeStoreView(Graph):
        _turbo_native_graph = True

        def serialize(self, *args, **kwargs):
            raise AssertionError("Native Store graph must not be serialized into another runtime")

    native = NativeStoreView()
    native.add((EX.a, EX.p, Literal(1)))
    _, shapes = fixture()
    with pytest.raises(NotImplementedError, match="native Store"):
        if operation == "data-graph":
            DataGraph.from_rdflib_graph(native)
        elif operation == "validate":
            turbo.validate(native, shacl_graph=shapes)
        elif operation == "rules":
            turbo.shacl_rules(native, shacl_graph=shapes)
        elif operation == "compile":
            turbo.compile_shapes(native)
        elif operation == "input":
            input_graph(native, direct=True)
        else:
            merge_graph(Graph(), native)
