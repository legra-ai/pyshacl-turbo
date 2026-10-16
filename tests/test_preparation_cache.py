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
