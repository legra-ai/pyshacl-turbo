"""DataGraph must retain native owners instead of rejecting or serializing them."""

from contextlib import closing

import pytest
from pyshacl_turbo import CompiledShapes, RuleExpandRunner, Validator, shacl_rules, validate
from pyshacl_turbo.graph_abstraction import DataGraph
from rdflib import Graph as ReferenceGraph
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS, SH
from rdflib_turbo import Graph, StoreDataset

S = URIRef("urn:native-view:s")
P = URIRef("urn:native-view:p")


@pytest.mark.parametrize(
    "capability,message",
    [
        ("_validate_shared_shapes", "borrowed native validation"),
        ("_expand_shared_shapes", "borrowed native rules"),
        ("_compile_shared_shapes", "borrowed native compiler"),
    ],
)
def test_ordinary_datagraph_does_not_advertise_native_borrowing(capability, message):
    source = ReferenceGraph()
    source.add((S, P, Literal("ordinary")))
    wrapped = DataGraph.from_rdflib(source)
    with pytest.raises(AttributeError, match=message):
        getattr(wrapped, capability)
    assert not hasattr(wrapped, capability)
    assert set(source) == {(S, P, Literal("ordinary"))}


def test_native_clone_rename_fails_without_mutating_the_original_owner():
    with closing(Graph(identifier=URIRef("urn:original"))) as source:
        source.add((S, P, Literal("original")))
        wrapped = DataGraph.from_rdflib(source)
        with pytest.raises(NotImplementedError, match="Renaming a native cloned graph"):
            wrapped.clone(identifier=URIRef("urn:renamed"))
        assert source.identifier == URIRef("urn:original")
        assert set(source) == {(S, P, Literal("original"))}


@pytest.mark.parametrize("dataset", [False, True])
def test_native_datagraph_view_and_clone_keep_native_scope(dataset, monkeypatch):
    source = StoreDataset() if dataset else Graph(identifier=URIRef("urn:scope"))
    selected = source.graph(URIRef("urn:named")) if dataset else source
    selected.add((S, P, Literal("original")))
    if dataset:
        source.graph(URIRef("urn:empty"))

    def no_transport(*args, **kwargs):
        raise AssertionError("Native DataGraph must not serialize its base")

    monkeypatch.setattr(source, "serialize", no_transport)
    wrapped = DataGraph.from_rdflib(source)
    assert wrapped.impl is source
    assert wrapped.store is source.store
    assert wrapped.is_multigraph() is dataset
    clone = wrapped.clone()
    assert type(clone.impl) is type(source)
    assert clone.store is not source.store
    if dataset:
        assert set(clone.quads()) == set(source.quads())
        assert {g.identifier for g in clone.graphs()} == {g.identifier for g in source.graphs()}
    else:
        assert set(clone.triples((None, None, None))) == set(source)
        assert clone.impl.identifier == source.identifier
    clone.add((S, P, Literal("new")))
    assert (S, P, Literal("new")) not in source


@pytest.mark.parametrize("runner", [Validator, RuleExpandRunner])
@pytest.mark.parametrize("inplace", [False, True])
def test_public_runner_borrows_native_datagraph_without_transport(runner, inplace, monkeypatch):
    source = Graph()
    source.add((S, P, Literal("original")))
    shapes = ReferenceGraph()
    shape = URIRef("urn:shape")
    shapes.add((shape, SH.targetNode, S))
    shapes.add((shape, SH.property, URIRef("urn:property")))
    shapes.add((URIRef("urn:property"), SH.path, P))
    shapes.add((URIRef("urn:property"), SH.minCount, Literal(1)))
    rule = URIRef("urn:rule")
    shapes.add((shape, SH.rule, rule))
    for predicate, value in (
        (RDF.type, SH.TripleRule),
        (SH.subject, SH.this),
        (SH.predicate, URIRef("urn:flag")),
        (SH.object, Literal(True)),
    ):
        shapes.add((rule, predicate, value))

    def no_transport(*args, **kwargs):
        raise AssertionError("Native runner must not serialize its base")

    monkeypatch.setattr(source, "serialize", no_transport)
    instance = runner(
        DataGraph.from_rdflib(source), shacl_graph=shapes, options={"inplace": inplace}
    )
    result = instance.run()
    if runner is Validator:
        assert result[0] is True
    else:
        assert (S, URIRef("urn:flag"), Literal(True)) in result
        assert ((S, URIRef("urn:flag"), Literal(True)) in source) is inplace
    assert isinstance(instance.target_graph.impl, Graph)


@pytest.mark.parametrize("runner", [Validator, RuleExpandRunner])
@pytest.mark.parametrize("inplace", [False, True])
def test_native_runner_preinference_keeps_selected_owner(runner, inplace, monkeypatch):
    source = Graph()
    child, parent = URIRef("urn:Child"), URIRef("urn:Parent")
    source.add((S, RDF.type, child))
    source.add((child, RDFS.subClassOf, parent))
    shapes = ReferenceGraph()
    shape, rule = URIRef("urn:shape"), URIRef("urn:rule")
    shapes.add((shape, SH.targetClass, parent))
    shapes.add((shape, SH.rule, rule))
    for predicate, value in (
        (RDF.type, SH.TripleRule),
        (SH.subject, SH.this),
        (SH.predicate, URIRef("urn:flag")),
        (SH.object, Literal(True)),
    ):
        shapes.add((rule, predicate, value))

    def no_transport(*args, **kwargs):
        raise AssertionError("Native preinference must not serialize its base")

    monkeypatch.setattr(source, "serialize", no_transport)
    instance = runner(
        DataGraph.from_rdflib(source),
        shacl_graph=shapes,
        options={"inplace": inplace, "inference": "rdfs"},
    )
    instance.run()
    if runner is Validator:
        assert instance.target_graph.impl is source
        assert ((S, RDF.type, parent) in instance.target_graph.impl) is inplace
        assert instance.pre_inferenced is False
        assert instance.target_graph.store is source.store
        return
    assert (S, RDF.type, parent) in instance.target_graph.impl
    assert ((S, RDF.type, parent) in source) is inplace
    assert instance.pre_inferenced is True
    assert (instance.target_graph.store is source.store) is inplace


@pytest.mark.parametrize("compiled", [False, True])
@pytest.mark.parametrize("rules", [False, True])
def test_native_datagraph_direct_execution_borrows_instead_of_enumerating(
    compiled, rules, monkeypatch
):
    source = Graph()
    source.add((S, P, Literal("original")))
    shapes = ReferenceGraph()
    shape, rule = URIRef("urn:shape"), URIRef("urn:rule")
    shapes.add((shape, SH.targetNode, S))
    shapes.add((shape, SH.rule, rule))
    for predicate, value in (
        (RDF.type, SH.TripleRule),
        (SH.subject, SH.this),
        (SH.predicate, URIRef("urn:flag")),
        (SH.object, Literal(True)),
    ):
        shapes.add((rule, predicate, value))
    program = CompiledShapes(shapes, advanced=True) if compiled else None

    def no_enumeration(*args, **kwargs):
        raise AssertionError("Native DataGraph execution must borrow its owner")

    monkeypatch.setattr(source, "triples", no_enumeration)
    wrapped = DataGraph.from_rdflib(source)
    if rules:
        output = (
            program.shacl_rules(wrapped, inplace=True)
            if compiled
            else shacl_rules(wrapped, shacl_graph=shapes, inplace=True)
        )
        monkeypatch.undo()
        assert (S, URIRef("urn:flag"), Literal(True)) in output
    else:
        output = program.validate(wrapped) if compiled else validate(wrapped, shacl_graph=shapes)
        assert output[0] is True
