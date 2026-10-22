"""The facade supports a versioned optional runtime, with no conversion fallback.

Unit tests explicitly control provider capabilities on the current dataset class.
Cross-wheel tests in integration/ exercise the actual Rust provider.
"""

import json
from contextlib import nullcontext

import pyshacl_turbo as turbo
import pytest
import rdflib_turbo
from rdflib import Graph
from rdflib_turbo import _native as runtime

SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#> .
<urn:S> sh:targetNode <urn:s>; sh:class <urn:C>."""


def test_old_runtime_and_text_format_are_rejected_before_conversion(monkeypatch):
    monkeypatch.delattr(runtime, "SHARED_SHACL_PROTOCOL", raising=False)
    data = rdflib_turbo.Dataset()
    program = turbo.compile_shapes(SHAPES)
    with pytest.raises(RuntimeError, match="protocol 1"):
        program.validate(data)
    with pytest.raises(ValueError, match="data_graph_format"):
        program.validate(data, data_graph_format="turtle")
    with pytest.raises(NotImplementedError, match="owlrl-turbo"):
        turbo.validate(data, shacl_graph=SHAPES, inference="rdfs")


def test_protocol_one_source_requires_a_borrowed_validation_adapter(monkeypatch):
    data = rdflib_turbo.Dataset()
    program = turbo.compile_shapes(SHAPES)
    program._shared_program = object()
    monkeypatch.setattr(runtime, "SHARED_SHACL_PROTOCOL", 1, raising=False)
    monkeypatch.delattr(rdflib_turbo.Dataset, "_validate_shared_shapes", raising=False)
    monkeypatch.setattr(
        runtime, "SHACL_ENGINE_FINGERPRINT", turbo._native.SHACL_ENGINE_FINGERPRINT, raising=False
    )
    with pytest.raises(RuntimeError, match="borrowed SHACL validation"):
        program.validate(data)


def test_native_graph_focus_nodes_use_the_data_namespace_mapping():
    calls = []
    shapes = Graph().parse(data=SHAPES)
    shapes.bind("ex", "urn:shapes:")
    program = turbo.compile_shapes(shapes)
    expected = program.validate(Graph())
    report = expected[1].serialize(format="nt")

    class NativeGraphView(Graph):
        def _validate_shared_shapes(self, compiled, settings, inplace):
            calls.append(json.loads(settings))
            return nullcontext((expected[0], report, expected[2], []))

    data = NativeGraphView()
    data.bind("ex", "urn:data:")
    program._shared_program = object()
    program.validate(data, focus_nodes=["ex:s"])
    assert calls[0]["focus_nodes"] == ["urn:data:s"]


def test_facade_protocol_preserves_options_reports_reuse_and_failure_type(monkeypatch):
    data = rdflib_turbo.Dataset()
    calls = []
    expected = turbo.validate(Graph(), shacl_graph=SHAPES)
    report = expected[1].serialize(format="nt")

    class Failure(ValueError):
        pass

    class Program:
        def __init__(self, source, advanced, namespaces, numeric_booleans):
            calls.append((source, advanced, namespaces))
            self.failure = False

        def validate(self, native, settings, inplace):
            assert native is data._native
            if self.failure:
                raise Failure("test validation failure")
            calls.append((json.loads(settings), inplace))
            return expected[0], report, expected[2], []

    monkeypatch.setattr(runtime, "SHARED_SHACL_PROTOCOL", 1, raising=False)
    monkeypatch.setattr(runtime, "SharedShapes", Program, raising=False)
    monkeypatch.setattr(
        runtime, "SHACL_ENGINE_FINGERPRINT", turbo._native.SHACL_ENGINE_FINGERPRINT, raising=False
    )
    monkeypatch.setattr(runtime, "SharedValidationFailure", Failure, raising=False)
    monkeypatch.setattr(
        rdflib_turbo.Dataset, "namespaces", lambda self: iter([("ex", "urn:")]), raising=False
    )
    monkeypatch.setattr(
        rdflib_turbo.Dataset,
        "_validate_shared_shapes",
        lambda source, program, settings, inplace: nullcontext(
            program.validate(source._native, settings, inplace)
        ),
        raising=False,
    )
    program = turbo.compile_shapes(SHAPES)
    actual = program.validate(data, inplace=True, max_validation_depth=None, focus_nodes=["ex:s"])
    assert actual[0] == expected[0] and actual[2] == expected[2]
    program.validate(data)
    assert len(calls) == 3  # One compilation, two executions.
    assert calls[1][0]["focus_nodes"] == ["urn:s"]
    assert calls[1][0]["max_validation_depth"] == 15
    assert calls[1][1]
    program._shared_program.failure = True
    with pytest.raises(turbo.ValidationFailure, match="test validation failure"):
        program.validate(data)
    monkeypatch.setattr(runtime, "SHACL_ENGINE_FINGERPRINT", "different")
    with pytest.raises(RuntimeError, match="different SHACL engine"):
        program.validate(data)
