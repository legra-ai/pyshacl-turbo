"""Public rule results preserve the original live DataGraph view protocol."""

import importlib

import pytest
from rdflib import BNode, ConjunctiveGraph, Dataset, Graph, Literal, Namespace
from rdflib.namespace import RDF, SH

EX = Namespace("urn:public-rule-view:")


def inputs(kind):
    if kind.startswith("native"):
        from rdflib_turbo import Graph as NativeGraph
        from rdflib_turbo import StoreDataset

        if kind == "native-dataset":
            source = StoreDataset(default_union=True)
            source.graph(EX.empty)
            source.graph(EX.named).add((EX.namedValue, EX.p, Literal("named")))
        else:
            identifier = BNode("public-source") if kind == "native-blank" else EX.source
            source = NativeGraph(identifier=identifier)
    elif kind.startswith("dataset"):
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
    [
        (kind, None)
        for kind in (
            "graph",
            "dataset",
            "dataset-custom",
            "conjunctive",
            "native-graph",
            "native-blank",
            "native-dataset",
        )
    ]
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
        assert result.is_multigraph() == (kind.startswith("dataset") or kind == "native-dataset")
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


@pytest.mark.parametrize("inplace", [False, True])
@pytest.mark.parametrize("kind", ["graph", "native-graph", "native-dataset"])
def test_public_rules_preserve_an_existing_rdflib_datagraph_view(inplace, kind):
    observations = []
    for name in ("pyshacl", "pyshacl_turbo"):
        engine = importlib.import_module(name)
        cls = importlib.import_module(name + ".graph_abstraction").DataGraph
        source, shapes = inputs(kind)
        wrapped = cls.from_rdflib(source)
        result = engine.shacl_rules(wrapped, shacl_graph=shapes, inplace=inplace)
        assert isinstance(result, cls)
        assert ((EX.focus, EX.added, Literal(True)) in source) is inplace
        assert (result.default_graph.store is source.store) is inplace
        observations.append((result is wrapped, set(result.quads()), result.identifier))
    assert observations[0] == observations[1]


def test_public_native_view_reads_dataset_settings_before_rule_writes():
    from rdflib_turbo import StoreDataset

    observations = []
    for name in ("pyshacl", "pyshacl_turbo"):
        calls = []
        failure = ValueError("default union read after writes")

        class Source(StoreDataset):
            @property
            def default_union(self):
                if self.__dict__.get("armed", False):
                    self.probe_calls.append(len(self))
                    if len(self) > 1:
                        raise self.probe_failure
                return self.__dict__.get("_probe_union", False)

            @default_union.setter
            def default_union(self, value):
                self._probe_union = value

        _, shapes = inputs("graph")
        source = Source().add((EX.focus, RDF.type, EX.Person))
        source.probe_calls = calls
        source.probe_failure = failure
        source.armed = True
        result = importlib.import_module(name).shacl_rules(source, shacl_graph=shapes, inplace=True)
        assert result.impl is source
        observations.append((calls, set(result.quads()), len(source)))
    assert observations[0] == observations[1]


@pytest.mark.parametrize("inplace", [False, True])
def test_public_native_settings_failure_precedes_loading_shapes(tmp_path, inplace):
    from rdflib_turbo import StoreDataset

    class Source(StoreDataset):
        @property
        def default_union(self):
            if self.__dict__.get("armed", False):
                raise self.failure
            return False

        @default_union.setter
        def default_union(self, value):
            pass

    for name in ("pyshacl", "pyshacl_turbo"):
        source = Source().add((EX.focus, RDF.type, EX.Person))
        failure = ValueError("source setting failure")
        source.failure = failure
        source.armed = True
        with pytest.raises(ValueError) as raised:
            importlib.import_module(name).shacl_rules(
                source, shacl_graph=str(tmp_path / "missing.ttl"), inplace=inplace
            )
        assert raised.value is failure
        assert len(source) == 1
