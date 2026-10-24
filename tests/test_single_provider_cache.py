"""One-provider top-level calls reuse immutable programs and read fresh inputs."""

from types import SimpleNamespace

import pyshacl_turbo as turbo
import pytest
import rdflib_turbo as runtime
from rdflib import Graph, Literal, URIRef
from rdflib.compare import isomorphic
from rdflib_turbo import _native as provider

SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#>.
<urn:S> sh:targetNode <urn:s>; sh:property <urn:P>.
<urn:P> sh:path <urn:p>; sh:minCount 1.
"""
RULES = """@prefix sh: <http://www.w3.org/ns/shacl#>.
<urn:S> sh:targetNode <urn:s>; sh:rule <urn:R>.
<urn:R> a sh:TripleRule; sh:subject sh:this;
sh:predicate <urn:derived>; sh:object true.
"""


@pytest.fixture
def compilation(monkeypatch):
    turbo._compile_native.cache_clear()
    compiled, borrowed, direct = [], [], []
    constructor = turbo._native.CompiledShapes
    shared = provider.SharedShapes

    def compile_native(*args, _policy):
        assert _policy is turbo._native._REGEX_POLICY
        program = constructor.from_input(*args, _policy=_policy)
        compiled.append(program)
        return program

    class Shared:
        def __new__(cls, *args, _policy):
            assert _policy is provider.shacl._REGEX_POLICY
            direct.append(args)
            return shared(*args, _policy=_policy)

        @staticmethod
        def from_compiled(program):
            result = shared.from_compiled(program)
            assert result.shares_program(program)
            borrowed.append(program)
            return result

    monkeypatch.setattr(turbo._native, "CompiledShapes", SimpleNamespace(from_input=compile_native))
    monkeypatch.setattr(provider, "SharedShapes", Shared)
    yield compiled, borrowed, direct
    turbo._compile_native.cache_clear()


@pytest.mark.parametrize("factory", [Graph, runtime.Graph, runtime.Dataset])
def test_repeated_top_level_validation_reuses_exact_program(compilation, factory):
    shapes = Graph().parse(data=SHAPES, format="turtle")
    expected = []
    actual = []
    for text in ("<urn:s> <urn:p> 1.", "<urn:s> <urn:other> 2."):
        data = factory().parse(data=text, format="turtle")
        reference = Graph().parse(data=text, format="turtle")
        try:
            expected.append(turbo.validate(reference, shacl_graph=shapes))
            actual.append(turbo.validate(data, shacl_graph=shapes))
            assert actual[-1][0] == expected[-1][0]
            assert isomorphic(actual[-1][1], expected[-1][1])
            assert actual[-1][2] == expected[-1][2]
            assert len(data) == 1
        finally:
            if factory is runtime.Graph:
                data.close()
    compiled, borrowed, direct = compilation
    assert len(compiled) == 1
    assert direct == []
    if factory is not Graph:
        assert borrowed == [compiled[0], compiled[0]]
    assert [result[0] for result in actual] == [True, False]


@pytest.mark.parametrize("factory", [Graph, runtime.Dataset])
def test_repeated_rules_reuse_program_without_reusing_data(compilation, factory):
    shapes = Graph().parse(data=RULES, format="turtle")
    for value in (1, 2):
        data = factory().parse(data=f"<urn:s> <urn:p> {value}.", format="turtle")
        result = turbo.shacl_rules(data, shacl_graph=shapes, inplace=True)
        assert result is data
        graph = data.to_rdflib() if factory is runtime.Dataset else data
        expected = {
            (URIRef("urn:s"), URIRef("urn:derived"), Literal(True)),
            (URIRef("urn:s"), URIRef("urn:p"), Literal(value)),
        }
        if factory is runtime.Dataset:
            assert set(graph.quads((None, None, None, None))) == {
                (*triple, graph.default_graph.identifier) for triple in expected
            }
        else:
            assert set(graph) == expected
    compiled, borrowed, direct = compilation
    assert len(compiled) == 1
    assert direct == []
    if factory is runtime.Dataset:
        assert borrowed == [compiled[0], compiled[0]]


def test_cache_hit_reuses_cache_owned_typed_source():
    turbo._compile_native.cache_clear()
    first = turbo.compile_shapes(Graph().parse(data=SHAPES, format="turtle"))
    second = turbo.compile_shapes(Graph().parse(data=SHAPES, format="turtle"))
    assert first._native is second._native
    assert first._shared_spec[0] is second._shared_spec[0]
    assert first.graph is not second.graph
    turbo._compile_native.cache_clear()
    assert not first.validate(Graph())[0]


@pytest.mark.parametrize("factory", [runtime.Graph, runtime.Dataset])
def test_native_compilation_never_traverses_or_copies_data(factory):
    def forbidden(*args, **kwargs):
        raise AssertionError("native data traversed or copied in Python")

    class Source(factory):
        __iter__ = triples = quads = serialize = to_rdflib = copy = forbidden

    data = Source().parse(data="<urn:s> <urn:p> 1.", format="turtle")
    owner = data.store.backend._native
    try:
        for _ in range(2):
            assert turbo.validate(data, shacl_graph=SHAPES)[0]
            assert data.store.backend._native is owner
            assert len(data) == 1
    finally:
        if factory is runtime.Graph:
            data.close()


@pytest.mark.parametrize("factory", [runtime.Graph, runtime.Dataset])
def test_native_cache_invalidates_same_size_content_namespaces_and_flags(compilation, factory):
    from rdflib.namespace import SH

    shapes = Graph().parse(data=SHAPES, format="turtle")
    data = factory().parse(data="<urn:s> <urn:p> 1.", format="turtle")
    try:
        assert turbo.validate(data, shacl_graph=shapes)[0]
        size = len(shapes)
        assert turbo.validate(data, shacl_graph=shapes)[0]
        assert len(shapes) == size
        shapes.set((URIRef("urn:P"), SH.minCount, Literal(2)))
        assert len(shapes) == size
        assert not turbo.validate(data, shacl_graph=shapes)[0]
        shapes.bind("changed", URIRef("urn:changed:"))
        assert not turbo.validate(data, shacl_graph=shapes)[0]
        assert not turbo.validate(data, shacl_graph=shapes, advanced=True)[0]
    finally:
        if factory is runtime.Graph:
            data.close()
    compiled, borrowed, direct = compilation
    assert len(compiled) == 4
    assert borrowed == [compiled[0], compiled[0], *compiled[1:]]
    assert direct == []
