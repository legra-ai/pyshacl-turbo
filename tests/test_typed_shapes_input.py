"""Shape preparation uses exact immutable terms without RDF text roundtrips."""

import pyshacl_turbo as turbo
from rdflib import Dataset, Graph, URIRef

SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#>.
<urn:S> sh:targetNode <urn:s>; sh:property <urn:P>.
<urn:P> sh:path <urn:p>; sh:minCount 1.
"""


def test_preparation_key_contains_exact_terms_not_rdf_text():
    turbo._compile_native.cache_clear()
    program = turbo.compile_shapes(Graph().parse(data=SHAPES, format="turtle"))
    assert not isinstance(program._shared_spec[0], str)


def test_cache_miss_and_hit_never_use_text_compiler(monkeypatch):
    turbo._compile_native.cache_clear()
    native = turbo._native.CompiledShapes

    class DirectCompiler:
        def __new__(cls, *args, **kwargs):
            raise AssertionError("shape preparation invoked the RDF text compiler")

        @staticmethod
        def from_input(*args, _policy):
            assert _policy is turbo._native._REGEX_POLICY
            return native.from_input(*args, _policy=_policy)

    monkeypatch.setattr(turbo._native, "CompiledShapes", DirectCompiler)
    first = turbo.compile_shapes(Graph().parse(data=SHAPES, format="turtle"))
    second = turbo.compile_shapes(Graph().parse(data=SHAPES, format="turtle"))
    assert first._native is second._native
    assert first._shared_spec[0] is second._shared_spec[0]
    assert not first.validate(Graph())[0]
    turbo._compile_native.cache_clear()


def test_dataset_shape_key_keeps_graph_placement_and_empty_contexts():
    turbo._compile_native.cache_clear()
    left, right = Dataset(), Dataset()
    left.graph(URIRef("urn:a")).parse(data=SHAPES, format="turtle")
    right.graph(URIRef("urn:b")).parse(data=SHAPES, format="turtle")
    first, second = turbo.compile_shapes(left), turbo.compile_shapes(right)
    assert first._shared_spec[0] != second._shared_spec[0]
    right.graph(URIRef("urn:declared-empty"))
    third = turbo.compile_shapes(right)
    assert third._shared_spec[0] != second._shared_spec[0]
    turbo._compile_native.cache_clear()


def test_contextless_shape_graphs_reuse_cache_across_random_identifiers():
    turbo._compile_native.cache_clear()
    first = turbo.compile_shapes(Graph().parse(data=SHAPES, format="turtle"))
    second = turbo.compile_shapes(Graph().parse(data=SHAPES, format="turtle"))
    assert first._native is second._native
    assert turbo._compile_native.cache_info().hits == 1
    turbo._compile_native.cache_clear()
