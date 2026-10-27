"""Automatic compilation reuse must never reuse mutable input or query results."""

from types import SimpleNamespace

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

    def compile_native(*args, _policy):
        assert _policy is turbo._native._REGEX_POLICY
        calls.append(args)
        return native.from_input(*args, _policy=_policy)

    monkeypatch.setattr(turbo._native, "CompiledShapes", SimpleNamespace(from_input=compile_native))
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
        patch.setattr(turbo._native, "CompiledShapes", SimpleNamespace(from_input=forbidden))
        for term_type in (URIRef, BNode, Literal):
            patch.setattr(term_type, "n3", forbidden)
        second = turbo.compile_shapes(source)
    assert second._native is first._native
    assert turbo._compile_native.cache_info().hits == 1


def test_reordered_datasets_reuse_source_but_contextless_union_has_a_distinct_key():
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
    reordered_dataset = Dataset(default_union=True)
    for prefix, namespace in dataset.namespaces():
        reordered_dataset.bind(prefix, namespace)
    for context in (EX.second, EX.first):
        for triple in reversed(list(source)):
            reordered_dataset.graph(context).add(triple)
    third = turbo.compile_shapes(reordered_dataset)
    # Equal unions do not imply equal named GRAPH inputs. Record ordering within
    # the same complete dataset remains irrelevant to the immutable cache key.
    assert first._native is not second._native
    assert first._native is third._native
    assert first._blank_nodes[str(blank)] is blank
    assert first.targeting(graph(""), EX.s) == [blank]
    assert second.targeting(graph(""), EX.s) == [blank]


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


def test_native_shapes_key_preserves_exact_terms_and_full_dataset_placement():
    from pyshacl_turbo.rdf import shape_batches, shape_graphs
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
    canonical = turbo._native.ShapesInput(shape_batches(source, {}), True, shape_graphs(source, {}))
    # Four exact values in each of two contexts, plus two declared named graphs.
    assert len(canonical) == 2 * len(values) + 2
    assert canonical == turbo._native.ShapesInput(
        shape_batches(source, {}), True, shape_graphs(source, {})
    )
    assert canonical != turbo._native.ShapesInput(shape_batches(shapes, {}))
    changed = Dataset(default_union=True)
    changed.graph(EX.first).__iadd__(shapes)
    for value in values:
        if value.datatype == XSD.string:
            changed.graph(EX.second).add((blank, SH.message, Literal(str(value))))
        else:
            changed.graph(EX.second).add((blank, SH.message, value))
    assert canonical != turbo._native.ShapesInput(
        shape_batches(changed, {}), True, shape_graphs(changed, {})
    )


def test_dataset_compilation_does_not_retain_context_only_python_owners():
    from rdflib import BNode, Dataset

    source = Dataset(default_union=True)
    context = BNode("context-only")
    shape = BNode("shape-node")
    source.graph(context).add((shape, SH.targetNode, EX.s))
    compiled = turbo.compile_shapes(source)
    assert compiled._blank_nodes == {str(shape): shape}
    assert compiled.targeting(graph(""), EX.s) == [shape]


@pytest.mark.parametrize("position", [0, 1, 2])
def test_graph_first_blank_reused_in_statement_keeps_its_real_python_owner(position):
    from pyshacl_turbo.term_input import _TermBatch
    from rdflib import BNode

    node = BNode("context-then-statement")
    nodes = {}
    batch = _TermBatch(nodes)
    context_index = batch.intern(node, retain_blank_owner=False)
    assert nodes == {}
    statement = [EX.s, EX.p, EX.value]
    statement[position] = node
    batch.append(*statement, node, retain_graph_owner=False)
    assert batch.quads[0][position] == context_index
    assert nodes[str(node)] is node


def test_data_transfer_keeps_its_existing_default_graph_owner_behavior():
    from pyshacl_turbo.term_input import _TermBatch
    from rdflib import BNode

    node = BNode("data-context")
    nodes = {}
    _TermBatch(nodes).append(EX.s, EX.p, EX.value, node)
    assert nodes[str(node)] is node


def test_native_shapes_key_rejects_malformed_term_batches():
    with pytest.raises(ValueError, match="Invalid shapes term record"):
        turbo._native.ShapesInput(iter([([(99, "invalid", None, None)], [])]))


def test_compilation_releases_transfer_batch_before_native_compile(monkeypatch):
    import weakref

    from pyshacl_turbo import rdf

    original_batch = rdf._TermBatch
    original_compile = turbo._native.CompiledShapes
    snapshots = []

    class TrackedBatch(original_batch):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            snapshots.append(weakref.ref(self))

    def compile_native(*args, _policy):
        assert _policy is turbo._native._REGEX_POLICY
        assert snapshots and all(snapshot() is None for snapshot in snapshots), (
            "Typed transfer batch outlived canonicalization"
        )
        return original_compile.from_input(*args, _policy=_policy)

    monkeypatch.setattr(rdf, "_TermBatch", TrackedBatch)
    monkeypatch.setattr(turbo._native, "CompiledShapes", SimpleNamespace(from_input=compile_native))
    turbo.compile_shapes(graph("ex:ReleasedBatch sh:targetNode ex:s."))


@pytest.mark.parametrize("dataset", [False, True])
def test_shape_transfer_batches_are_bounded_and_preserve_blank_identity(dataset):
    from pyshacl_turbo.rdf import shape_batches
    from rdflib import BNode, Dataset

    source = graph("")
    shape = BNode("batched-shape")
    for index in range(513):
        source.add((shape, SH.targetNode, EX[f"node{index}"]))
    if dataset:
        named = Dataset(default_union=True)
        named.graph(BNode("context-only")).__iadd__(source)
        named.graph(EX.second).__iadd__(source)
        source = named
    nodes = {}
    batches = list(shape_batches(source, nodes))
    assert all(0 < len(quads) <= 256 for records, quads in batches)
    assert all(len(records) <= 4 * 256 for records, quads in batches)
    assert sum(len(quads) for records, quads in batches) == 513 * (2 if dataset else 1)
    assert all((g is not None) == dataset for records, quads in batches for s, p, o, g in quads)
    assert nodes == {str(shape): shape}
    key = turbo._native.ShapesInput(iter(batches), dataset)
    assert len(key) == 513 * (2 if dataset else 1) + (2 if dataset else 0)


def test_invalid_late_shape_batch_does_not_cache_partial_compilation(monkeypatch):
    from pyshacl_turbo.rdf import input_graph

    shapes = graph("ex:LateBatch sh:targetNode ex:s.")
    valid = input_graph(shapes, direct=True).source

    def invalid_batches(*args):
        yield valid
        yield [], [(0, 0, 0, None)]

    with monkeypatch.context() as patch:
        patch.setattr(turbo, "shape_batches", invalid_batches)
        with pytest.raises(ValueError, match="Invalid shapes term index"):
            turbo.compile_shapes(shapes)
    assert turbo._compile_native.cache_info().currsize == 0
    assert turbo.compile_shapes(shapes).targeting(graph(""), EX.s) == [EX.LateBatch]


@pytest.mark.parametrize(
    "batch",
    [([], [(0, 0, 0, None)] * 257), ([(0, "urn:s", None, None)] * 1025, [])],
)
def test_typed_shapes_rejects_oversized_transfer_batches(batch):
    with pytest.raises(ValueError, match="256"):
        turbo._native.ShapesInput(iter([batch]))


def test_compilation_reads_namespace_metadata_once(monkeypatch):
    shapes = graph("ex:MetadataOnce sh:targetNode ex:s.")
    original = shapes.namespaces
    calls = []

    def namespaces():
        calls.append(None)
        return original()

    monkeypatch.setattr(shapes, "namespaces", namespaces)
    turbo.compile_shapes(shapes)
    assert len(calls) == 1
