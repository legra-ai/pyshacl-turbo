"""Unsupported inference combinations reject without accepting caller mutations."""

import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Literal, Namespace
from rdflib_turbo import Graph as NativeGraph

EX = Namespace("urn:inference-boundary:")
SHAPES = """@prefix sh:<http://www.w3.org/ns/shacl#>.
<urn:Shape> sh:targetNode <urn:inference-boundary:s>;
 sh:property [sh:path <urn:inference-boundary:p>;sh:minCount 1]."""


def test_compiled_reference_graph_inference_rejects_without_mutation():
    data = Graph()
    data.bind("ex", EX)
    data.add((EX.s, EX.p, Literal("original")))
    shapes = Graph().parse(data=SHAPES, format="turtle")
    compiled = turbo.compile_shapes(shapes)
    before = set(data), tuple(data.namespaces()), set(shapes), tuple(shapes.namespaces())
    with pytest.raises(NotImplementedError, match="pre-inference requires a native source"):
        compiled.validate(data, inference="rdfs", inplace=True)
    assert before == (set(data), tuple(data.namespaces()), set(shapes), tuple(shapes.namespaces()))


def test_native_dash_inference_rejects_before_engine_or_owner_mutation(monkeypatch):
    def unexpected_engine_call(*args, **kwargs):
        raise AssertionError("Unsupported inference must reject before engine execution")

    data = NativeGraph()
    try:
        data.bind("ex", EX)
        data.add((EX.s, EX.p, Literal("original")))
        shapes = Graph().parse(data=SHAPES, format="turtle")
        owner = data.store.backend._native
        namespace_revision = data.store._namespaces.revision
        before = set(data), tuple(data.namespaces()), set(shapes), tuple(shapes.namespaces())
        monkeypatch.setattr(turbo, "_compile_native", unexpected_engine_call)
        monkeypatch.setattr(NativeGraph, "_validate_shared_shapes", unexpected_engine_call)
        with pytest.raises(NotImplementedError, match="pre-inference with check_dash_result"):
            turbo.validate(
                data, shacl_graph=shapes, check_dash_result=True, inference="rdfs", inplace=True
            )
        assert data.store.backend._native is owner
        assert data.store._namespaces.revision == namespace_revision
        assert before == (
            set(data),
            tuple(data.namespaces()),
            set(shapes),
            tuple(shapes.namespaces()),
        )
    finally:
        data.close()
