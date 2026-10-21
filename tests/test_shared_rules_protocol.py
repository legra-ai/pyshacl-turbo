"""Native rule expansion keeps dataset ownership inside its shared runtime."""

import json

import pyshacl_turbo as turbo
import pytest
import rdflib_turbo
from rdflib_turbo import _native as runtime

SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#> .
<urn:S> sh:targetNode <urn:s>; sh:class <urn:C>."""


@pytest.fixture
def provider(monkeypatch):
    calls = []

    class Failure(ValueError):
        pass

    class Program:
        def __init__(self, *args):
            calls.append(("compile", args))
            self.failure = False
            self.invalid = False

        def expand(self, native, settings, inplace):
            if self.failure:
                raise Failure("rule expansion failed")
            calls.append((native, json.loads(settings), inplace))
            result = None if inplace else runtime.NativeDataset()
            if self.invalid:
                result = runtime.NativeDataset() if inplace else None
            return result, []

        def validate(self, native, settings, inplace):
            return True, "", "Validation Report\nConforms: True\n", []

    monkeypatch.setattr(runtime, "SHARED_SHACL_PROTOCOL", 1, raising=False)
    monkeypatch.setattr(runtime, "SharedShapes", Program, raising=False)
    monkeypatch.setattr(runtime, "SharedValidationFailure", Failure, raising=False)
    monkeypatch.setattr(
        runtime, "SHACL_ENGINE_FINGERPRINT", turbo._native.SHACL_ENGINE_FINGERPRINT, raising=False
    )
    monkeypatch.setattr(
        rdflib_turbo.Dataset, "namespaces", lambda self: iter([("ex", "urn:")]), raising=False
    )
    return calls


@pytest.mark.parametrize("inplace", [False, True])
def test_native_rules_preserve_wrapper_ownership_options_and_compilation(provider, inplace):
    data = rdflib_turbo.Dataset()
    program = turbo.compile_shapes(SHAPES)
    original = data._native
    result = program.shacl_rules(
        data,
        inplace=inplace,
        iterate_rules=True,
        max_rule_iterations=4,
        max_validation_depth=None,
        focus_nodes=["ex:s"],
        use_shapes=["urn:S"],
    )
    assert isinstance(result, rdflib_turbo.Dataset)
    assert (result is data) is inplace
    assert data._native is original
    if not inplace:
        assert result._native is not original
    native, settings, actual_inplace = provider[1]
    assert native is original and actual_inplace is inplace
    assert settings == {
        "iterate_rules": True,
        "max_rule_iterations": 4,
        "max_validation_depth": 15,
        "focus_nodes": ["urn:s"],
        "use_shapes": ["urn:S"],
    }
    program.validate(data)
    program.shacl_rules(data)
    assert sum(call[0] == "compile" for call in provider) == 1


def test_native_rules_guard_protocol_format_and_engine_before_conversion(provider, monkeypatch):
    program = turbo.compile_shapes(SHAPES)
    data = rdflib_turbo.Dataset()
    with pytest.raises(ValueError, match="data_graph_format"):
        program.shacl_rules(data, data_graph_format="turtle")
    monkeypatch.setattr(runtime, "SHARED_SHACL_PROTOCOL", 0)
    with pytest.raises(RuntimeError, match="protocol 1"):
        program.shacl_rules(data)
    monkeypatch.setattr(runtime, "SHARED_SHACL_PROTOCOL", 1)
    monkeypatch.setattr(runtime, "SHACL_ENGINE_FINGERPRINT", "different")
    with pytest.raises(RuntimeError, match="different SHACL engine"):
        program.shacl_rules(data)
    assert not provider


def test_native_rules_translate_failure_without_replacing_dataset(provider):
    data = rdflib_turbo.Dataset()
    program = turbo.compile_shapes(SHAPES)
    program.shacl_rules(data)
    program._shared_program.failure = True
    original = data._native
    with pytest.raises(turbo.ValidationFailure, match="rule expansion failed"):
        program.shacl_rules(data, inplace=True)
    assert data._native is original


def test_compiled_rules_do_not_convert_or_copy_native_input(provider, monkeypatch):
    data = rdflib_turbo.Dataset()
    program = turbo.compile_shapes(SHAPES)

    def forbidden(*args, **kwargs):
        raise AssertionError("native rules must stay in the dataset-owning runtime")

    monkeypatch.setattr(turbo, "_input", forbidden)
    for name in ("serialize", "to_rdflib", "from_rdflib", "copy"):
        monkeypatch.setattr(rdflib_turbo.Dataset, name, forbidden, raising=False)
    assert program.shacl_rules(data, inplace=True) is data
    assert isinstance(program.shacl_rules(data), rdflib_turbo.Dataset)


def test_public_rules_forward_native_input_without_replacing_wrapper(provider):
    data = rdflib_turbo.Dataset()
    assert turbo.shacl_rules(data, shacl_graph=SHAPES, inplace=True) is data


@pytest.mark.parametrize("inplace", [False, True])
def test_native_rules_reject_invalid_provider_ownership_result(provider, inplace):
    data = rdflib_turbo.Dataset()
    program = turbo.compile_shapes(SHAPES)
    program.shacl_rules(data)
    program._shared_program.invalid = True
    with pytest.raises(RuntimeError, match="expansion result"):
        program.shacl_rules(data, inplace=inplace)
