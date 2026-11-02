"""Public rule results preserve the original live DataGraph view protocol."""

import importlib

import pytest
from rdflib import ConjunctiveGraph, Dataset, Graph, Literal, Namespace
from rdflib.namespace import RDF, SH

EX = Namespace("urn:public-rule-view:")


def inputs(kind):
    if kind.startswith("dataset"):
        source = Dataset(default_union=True)
        if kind == "dataset-custom":
            source.default_graph = source.graph(EX.default)
        source.graph(EX.empty)
        source.graph(EX.named).add((EX.namedValue, EX.p, Literal("named")))
    elif kind == "conjunctive":
        source = ConjunctiveGraph(identifier=EX.source)
    else:
        source = Graph(identifier=EX.source)
    source.add((EX.focus, RDF.type, EX.Person))
    shapes = Graph()
    for triple in (
        (EX.S, SH.targetNode, EX.focus),
        (EX.S, SH.rule, EX.rule),
        (EX.rule, RDF.type, SH.TripleRule),
        (EX.rule, SH.subject, SH.this),
        (EX.rule, SH.predicate, EX.added),
        (EX.rule, SH.object, Literal(True)),
    ):
        shapes.add(triple)
    return source, shapes


@pytest.mark.parametrize(
    "kind,inference",
    [(kind, None) for kind in ("graph", "dataset", "dataset-custom", "conjunctive")]
    + [(kind, "rdfs") for kind in ("graph", "conjunctive")],
)
@pytest.mark.parametrize("inplace", [False, True])
def test_public_rules_return_live_view_with_reference_scope_and_mutation(kind, inplace, inference):
    observed = []
    for name in ("pyshacl", "pyshacl_turbo"):
        engine = importlib.import_module(name)
        cls = importlib.import_module(name + ".graph_abstraction").DataGraph
        source, shapes = inputs(kind)
        before = set(source.triples((None, None, None)))
        result = engine.shacl_rules(
            source, shacl_graph=shapes, inplace=inplace, inference=inference
        )
        assert isinstance(result, cls)
        assert result is not source
        assert result.is_multigraph() == kind.startswith("dataset")
        rows = list(result)
        assert all(len(row) == 4 for row in rows)
        assert set(rows) == set(result.quads())
        closure = set(result.triples((None, None, None)))
        assert before | {(EX.focus, EX.added, Literal(True))} <= closure
        if inference is None:
            assert closure == before | {(EX.focus, EX.added, Literal(True))}
        assert ((EX.focus, EX.added, Literal(True)) in source) is inplace
        if inplace:
            assert result.default_graph.store is source.store
        result.add((EX.extra, EX.p, EX.o))
        assert ((EX.extra, EX.p, EX.o) in source) is inplace
        observed.append(
            (
                result.is_multigraph(),
                result.identifier,
                set(result.quads()),
                {graph.identifier for graph in result.graphs()},
            )
        )
    assert observed[0] == observed[1]
