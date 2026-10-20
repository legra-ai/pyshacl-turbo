"""Automatic compilation reuse must never reuse mutable input or query results."""

import pyshacl_turbo as turbo
import pytest
from rdflib import Literal
from rdflib.namespace import SH
from test_compatibility import EX, graph


@pytest.fixture(autouse=True)
def isolated_compilation_cache():
    turbo._compile_native.cache_clear()
    yield
    turbo._compile_native.cache_clear()


def test_repeated_top_level_calls_share_native_compilation_and_read_fresh_data(monkeypatch):
    shapes = graph("""ex:S sh:targetNode ex:s; sh:sparql [
      sh:select "SELECT $this WHERE { $this ex:p ?v }"].""")
    native = turbo._native.CompiledShapes
    calls = []

    def compile_native(*args):
        calls.append(args)
        return native(*args)

    monkeypatch.setattr(turbo._native, "CompiledShapes", compile_native)
    assert turbo.validate(graph(""), shacl_graph=shapes)[0]
    assert not turbo.validate(graph("ex:s ex:p 1."), shacl_graph=shapes)[0]
    assert len(calls) == 1


def test_shape_mutation_invalidates_native_compilation():
    shapes = graph("ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1.")
    first = turbo.compile_shapes(shapes)
    shapes.set((EX.S, SH.minCount, Literal(2)))
    second = turbo.compile_shapes(shapes)
    data = graph("ex:s ex:p 1.")
    assert first.validate(data)[0]
    assert not second.validate(data)[0]
    assert first._native is not second._native


def test_equal_graph_contents_reuse_compilation_independently_of_graph_identity():
    text = "ex:CacheEquality sh:targetNode ex:s; sh:path ex:p; sh:minCount 1."
    first = turbo.compile_shapes(graph(text))
    second = turbo.compile_shapes(graph(text))
    assert first is not second
    assert first.graph is not second.graph
    assert first._native is second._native


def test_prefix_changes_and_advanced_configuration_do_not_share_statements():
    shapes = graph("""ex:CachePrefixes sh:targetNode ex:s; sh:sparql [
      sh:select "SELECT $this WHERE { $this custom:p ?v }"].""")
    shapes.bind("custom", "urn:first:")
    first = turbo.compile_shapes(shapes)
    shapes.bind("custom", "urn:second:", replace=True)
    second = turbo.compile_shapes(shapes)
    data = graph("ex:s <urn:first:p> 1.")
    assert not first.validate(data)[0]
    assert second.validate(data)[0]
    assert first._native is not second._native
    advanced = turbo.compile_shapes(shapes, advanced=True)
    assert advanced._native is not second._native


def test_compilation_failures_are_not_cached():
    shapes = graph("""ex:CacheFailure sh:targetNode ex:s;
      sh:sparql [sh:select "INVALID QUERY"].""")
    with pytest.raises(ValueError, match="SPARQL"):
        turbo.compile_shapes(shapes)
    constraint = next(shapes.objects(EX.CacheFailure, SH.sparql))
    shapes.set((constraint, SH.select, Literal("SELECT $this WHERE {}")))
    assert not turbo.compile_shapes(shapes).validate(graph(""))[0]


def test_reused_rule_statements_use_current_data_and_leave_inputs_independent():
    shapes = graph("""ex:CachedRule sh:targetNode ex:s; sh:rule ex:CopyRule.
      ex:CopyRule a sh:SPARQLRule;
      sh:construct "CONSTRUCT { $this ex:derived ?v } WHERE { $this ex:value ?v }".""")
    for value in [1, 2]:
        data = graph(f"ex:s ex:value {value}.")
        output = turbo.shacl_rules(data, shacl_graph=shapes)
        assert set(output.objects(EX.s, EX.derived)) == {Literal(value)}
        assert (EX.s, EX.derived, None) not in data
    assert turbo._compile_native.cache_info().hits == 1


def test_compilation_cache_is_bounded_and_reloads_evicted_shapes():
    first_graph = graph("ex:FirstCachedShape sh:targetNode ex:s.")
    first = turbo.compile_shapes(first_graph)
    for index in range(128):
        turbo.compile_shapes(graph(f"ex:OtherShape{index} sh:targetNode ex:s."))
    assert turbo._compile_native.cache_info().currsize == 128
    assert turbo.compile_shapes(first_graph)._native is not first._native
    assert first.validate(graph(""))[0]


def test_compilation_reuse_keeps_document_and_graph_boolean_semantics_separate():
    text = "ex:CacheBoolean sh:targetNode ex:s; sh:closed true."
    direct = turbo.compile_shapes(graph(text))
    from_document = turbo.compile_shapes(graph(text).serialize(format="turtle"))
    assert direct._native is not from_document._native


@pytest.mark.parametrize("dataset", [False, True])
def test_compilation_hits_avoid_python_serialization_and_union_copies(dataset, monkeypatch):
    from pyshacl_turbo import rdf
    from rdflib import BNode, Dataset, Graph, URIRef

    source = graph('ex:FastCache sh:targetNode ex:s; sh:message "message".')
    source.add((BNode("cache-blank"), SH.targetNode, EX.s))
    if dataset:
        named = Dataset(default_union=True)
        named.graph(EX.context).__iadd__(source)
        source = named
    first = turbo.compile_shapes(source)

    def forbidden(*args, **kwargs):
        raise AssertionError("Compilation cache hits must inspect terms without text conversion")

    with monkeypatch.context() as patch:
        patch.setattr(Graph, "serialize", forbidden)
        patch.setattr(rdf, "union", forbidden)
        patch.setattr(turbo._native, "CompiledShapes", forbidden)
        for term_type in (URIRef, BNode, Literal):
            patch.setattr(term_type, "n3", forbidden)
        second = turbo.compile_shapes(source)
    assert second._native is first._native
    assert turbo._compile_native.cache_info().hits == 1


def test_dataset_union_and_reordered_graph_share_exact_cache_contents():
    from rdflib import BNode, Dataset, Graph

    source = graph('ex:UnionCache sh:targetSubjectsOf ex:p; sh:message "message".')
    blank = BNode("stable-cache-shape")
    source.add((blank, SH.targetNode, EX.s))
    dataset = Dataset(default_union=True)
    dataset.graph(EX.first).__iadd__(source)
    dataset.graph(EX.second).__iadd__(source)
    reordered = Graph()
    for prefix, namespace in dataset.namespaces():
        reordered.bind(prefix, namespace)
    for triple in reversed(list(source)):
        reordered.add(triple)
    first = turbo.compile_shapes(dataset)
    second = turbo.compile_shapes(reordered)
    assert first._native is second._native
    assert first._blank_nodes[str(blank)] is blank
    assert first.targeting(graph(""), EX.s) == [blank]


@pytest.mark.parametrize("dataset", [False, True])
def test_exact_cache_key_tracks_literal_and_shared_store_mutations(dataset):
    from rdflib import Dataset, Graph
    from rdflib.namespace import XSD

    source = graph('ex:ExactCache sh:targetNode ex:s; sh:path ex:p; sh:hasValue "value".')
    owner = Dataset(default_union=True) if dataset else source
    if dataset:
        owner.graph(EX.named).__iadd__(source)
        mutable = owner.graph(EX.named)
    else:
        mutable = Graph(store=source.store, identifier=source.identifier)
    first = turbo.compile_shapes(owner)
    original_count = len(mutable)
    typed = Literal("value", datatype=XSD.string, normalize=False)
    mutable.set((EX.ExactCache, SH.hasValue, typed))
    second = turbo.compile_shapes(owner)
    assert len(mutable) == original_count
    assert first._native is not second._native
    assert first.validate(graph('ex:s ex:p "value".'))[0]
    typed_data = graph("")
    typed_data.add((EX.s, EX.p, typed))
    assert second.validate(typed_data)[0]
    assert not second.validate(graph('ex:s ex:p "value".'))[0]


def test_compilation_snapshot_rejects_non_rdf_terms():
    from rdflib import Variable

    shapes = graph("")
    shapes.add((EX.InvalidShape, SH.message, Variable("unsupported")))
    with pytest.raises(TypeError, match="RDFLib IRI, blank node or literal"):
        turbo.compile_shapes(shapes)


def test_native_shapes_key_preserves_exact_terms_and_deduplicates_union():
    from pyshacl_turbo.rdf import decode, input_graph
    from rdflib import BNode, Dataset
    from rdflib.namespace import XSD

    shapes = graph("")
    blank = BNode("canonical-shape")
    values = [
        Literal('quote " and newline\n漢字'),
        Literal("value", datatype=XSD.string),
        Literal("01", datatype=XSD.integer, normalize=False),
        Literal("message", lang="fr"),
    ]
    for value in values:
        shapes.add((blank, SH.message, value))
    source = Dataset(default_union=True)
    source.graph(EX.first).__iadd__(shapes)
    source.graph(EX.second).__iadd__(shapes)
    canonical = turbo._native.canonical_shapes(input_graph(source, direct=True).source)
    assert set(decode(canonical, preserve_ids=True)) == set(shapes)
    assert canonical == turbo._native.canonical_shapes(input_graph(shapes, direct=True).source)
