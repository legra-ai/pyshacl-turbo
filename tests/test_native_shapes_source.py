"""Native shapes compilation pins graph scope, namespaces and actual provider classes."""

import pyshacl_turbo as turbo
import pytest
from rdflib import RDF, BNode, Graph, Namespace, URIRef
from rdflib_turbo import Graph as NativeGraph
from rdflib_turbo import StoreDataset
from rdflib_turbo import _native as provider
from rdflib_turbo.graph import RDFLibStore

SH = Namespace("http://www.w3.org/ns/shacl#")
EX = Namespace("urn:native-shapes:")


def add_shape(graph, shape=EX.shape, focus=EX.focus):
    graph.add((shape, SH.targetNode, focus))
    graph.add((shape, SH["class"], EX.Required))


def report_focus(compiled, **settings):
    conforms, report, _ = compiled.validate(Graph(), **settings)
    assert conforms is False
    return set(report.objects(None, SH.focusNode)), report


def test_namespaces_changed_during_actual_native_compilation_are_rejected(monkeypatch):
    source = StoreDataset()
    shapes = source.default_graph
    add_shape(shapes)
    backend = source.store.backend
    original = backend._native
    calls = []

    class DelegatingStore:
        def __getattr__(self, name):
            return getattr(original, name)

        def compile_shapes(self, *args, _policy):
            assert _policy is provider.shacl._REGEX_POLICY
            program = original.compile_shapes(*args, _policy=_policy)
            calls.append(program)
            shapes.bind("changed", EX.changed)
            return program

    try:
        with monkeypatch.context() as context:
            context.setattr(backend, "_native", DelegatingStore())
            with pytest.raises(RuntimeError, match="namespaces changed while compiling"):
                turbo.CompiledShapes(shapes)
        assert len(calls) == 1
        assert isinstance(calls[0], provider.shacl.CompiledShapes)
    finally:
        source.close()


def test_captured_namespaces_and_program_survive_rebind_mutation_and_owner_close():
    source = StoreDataset()
    shapes = source.default_graph
    shapes.bind("chosen", EX, replace=True)
    add_shape(shapes)
    compiled = turbo.CompiledShapes(shapes)
    assert isinstance(compiled._native, provider.shacl.CompiledShapes)
    assert type(compiled._native) is turbo._native.CompiledShapes
    shared = provider.SharedShapes.from_compiled(compiled._native)
    assert shared.shares_program(compiled._native)
    shapes.bind("chosen", Namespace("urn:replacement:"), replace=True)
    shapes.set((EX.shape, SH.targetNode, EX.replacement_focus))
    source.close()

    focuses, report = report_focus(compiled, use_shapes=["chosen:shape"])
    assert focuses == {EX.focus}
    assert dict(report.namespaces())["chosen"] == URIRef(EX)


def test_compilation_of_closed_native_shapes_owner_fails():
    source = StoreDataset()
    shapes = source.default_graph
    add_shape(shapes)
    source.close()
    with pytest.raises(RuntimeError, match="closed"):
        turbo.CompiledShapes(shapes)


def test_committed_owner_compilation_during_pending_transaction_excludes_pending_shapes():
    source = StoreDataset()
    add_shape(source.default_graph)
    try:
        with source.transaction() as pending:
            add_shape(pending.default_graph, EX.pending_shape, EX.pending_focus)
            compiled = turbo.CompiledShapes(source.default_graph)
            focuses, _ = report_focus(compiled)
            assert focuses == {EX.focus}
        # The existing program owns its earlier committed read version even
        # after the transaction containing the second shape is committed.
        focuses, _ = report_focus(compiled)
        assert focuses == {EX.focus}
        fresh_focuses, _ = report_focus(turbo.CompiledShapes(source.default_graph))
        assert fresh_focuses == {EX.focus, EX.pending_focus}
    finally:
        source.close()


@pytest.mark.parametrize("selected", (URIRef("urn:equal-graph"), BNode("urn:equal-graph")))
def test_selected_named_and_blank_graphs_with_equal_lexical_labels_stay_isolated(selected):
    source = StoreDataset()
    named = source.graph(URIRef("urn:equal-graph"))
    blank = source.graph(BNode("urn:equal-graph"))
    add_shape(named, EX.named_shape, EX.named_focus)
    add_shape(blank, EX.blank_shape, EX.blank_focus)
    try:
        focuses, _ = report_focus(turbo.CompiledShapes(source.graph(selected)))
        assert focuses == ({EX.named_focus} if isinstance(selected, URIRef) else {EX.blank_focus})
    finally:
        source.close()


def test_custom_default_identifier_is_selected_as_default_without_matching_named_context():
    identifier = URIRef("urn:custom-default")
    store = RDFLibStore(default_identifier=identifier)
    default = NativeGraph(store=store, identifier=identifier, bind_namespaces="none")
    named = NativeGraph(
        store=store, identifier=URIRef("urn:x-rdflib:default"), bind_namespaces="none"
    )
    add_shape(default, EX.default_shape, EX.default_focus)
    add_shape(named, EX.named_shape, EX.named_focus)
    try:
        focuses, _ = report_focus(turbo.CompiledShapes(default))
        assert focuses == {EX.default_focus}
        named_focuses, _ = report_focus(turbo.CompiledShapes(named))
        assert named_focuses == {EX.named_focus}
        data = Graph()
        data.add((EX.default_focus, RDF.type, EX.Required))
        assert turbo.CompiledShapes(default).validate(data)[0] is True
    finally:
        store.backend.close()
