"""Top-level native execution compiles shapes only in the data-owning provider."""

from contextlib import contextmanager
from types import SimpleNamespace

import pyshacl_turbo as turbo
import pytest
import rdflib_turbo
from pyshacl_turbo.errors import ShapeLoadError
from rdflib import Graph
from rdflib_turbo import _native as shared

SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#> .
<urn:S> sh:targetNode <urn:s>; sh:class <urn:C>."""


@pytest.fixture
def provider(monkeypatch):
    calls = []

    native = turbo._native.CompiledShapes
    shared_constructor = shared.SharedShapes

    class Program:
        @staticmethod
        def from_compiled(compiled, *, _comparison_policy):
            assert _comparison_policy is turbo._native._VALUE_COMPARISON_POLICY
            assert shared_constructor.from_compiled(
                compiled, _comparison_policy=_comparison_policy
            ).shares_program(compiled)
            return Program()

        def prepare_rules_transaction(self, native, settings, scope):
            assert scope is None
            calls.append(("expand", native))
            return SimpleNamespace(
                output=list, accept=lambda: calls.append(("accept-rules", native))
            )

    @contextmanager
    def validate(owner, program, settings, inplace):
        calls.append(("validate", owner))
        yield True, "", "Validation Report\nConforms: True\n", []
        calls.append(("accept", owner))

    def compile_native(*args, _policy):
        assert _policy is turbo._native._REGEX_POLICY
        calls.append(("compile", args))
        return native.from_input(*args, _policy=_policy)

    turbo._compile_native.cache_clear()
    monkeypatch.setattr(turbo._native, "CompiledShapes", SimpleNamespace(from_input=compile_native))
    monkeypatch.setattr(shared, "SharedShapes", Program)
    monkeypatch.setattr(shared, "SHACL_ENGINE_FINGERPRINT", turbo._native.SHACL_ENGINE_FINGERPRINT)
    monkeypatch.setattr(rdflib_turbo.Dataset, "_validate_shared_shapes", validate)
    return calls


@pytest.mark.parametrize("rules", [False, True])
def test_top_level_shared_execution_compiles_only_in_owner(provider, rules):
    data = rdflib_turbo.Dataset()
    if rules:
        assert turbo.shacl_rules(data, shacl_graph=SHAPES, inplace=True) is data
        assert [kind for kind, _ in provider] == ["compile", "expand", "accept-rules"]
    else:
        assert turbo.validate(data, shacl_graph=SHAPES)[0]
        assert [kind for kind, _ in provider] == ["compile", "validate", "accept"]


@pytest.mark.parametrize("rules", [False, True])
def test_shared_identity_failure_precedes_compilation(provider, monkeypatch, rules):
    monkeypatch.setattr(shared, "SHACL_ENGINE_FINGERPRINT", "different")
    operation = turbo.shacl_rules if rules else turbo.validate
    with pytest.raises(RuntimeError, match="different SHACL engine"):
        operation(rdflib_turbo.Dataset(), shacl_graph=SHAPES, inplace=True)
    assert not provider


@pytest.mark.parametrize("rules", [False, True])
def test_shared_compiler_failure_precedes_execution(provider, monkeypatch, rules):
    def invalid(*args, _policy):
        assert _policy is turbo._native._REGEX_POLICY
        raise ValueError("invalid shape path")

    monkeypatch.setattr(turbo._native, "CompiledShapes", SimpleNamespace(from_input=invalid))
    operation = turbo.shacl_rules if rules else turbo.validate
    with pytest.raises(ValueError, match="invalid shape path"):
        operation(rdflib_turbo.Dataset(), shacl_graph=SHAPES, inplace=True)
    assert not provider


def test_failed_report_decode_never_accepts_shared_output(provider, monkeypatch):
    def fail_decode(*args, **kwargs):
        raise ValueError("report decoding failed")

    monkeypatch.setattr(turbo, "_graph", fail_decode)
    with pytest.raises(ValueError, match="report decoding failed"):
        turbo.validate(rdflib_turbo.Dataset(), shacl_graph=SHAPES, inplace=True)
    assert [kind for kind, _ in provider] == ["compile", "validate"]


@pytest.mark.parametrize("rules", [False, True])
def test_shared_compile_failure_retains_public_failure_type(provider, monkeypatch, rules):
    def invalid(*args, _policy):
        assert _policy is turbo._native._REGEX_POLICY
        raise turbo.ValidationFailure("invalid shape declaration")

    monkeypatch.setattr(turbo._native, "CompiledShapes", SimpleNamespace(from_input=invalid))
    data = rdflib_turbo.Dataset()
    if rules:
        with pytest.raises(turbo.ValidationFailure, match="invalid shape declaration"):
            turbo.shacl_rules(data, shacl_graph=SHAPES, inplace=True)
    else:
        conforms, failure, text = turbo.validate(data, shacl_graph=SHAPES, inplace=True)
        assert not conforms
        assert isinstance(failure, turbo.ValidationFailure)
        assert "invalid shape declaration" in text
    assert not provider


@pytest.mark.parametrize("rules", [False, True])
def test_real_shared_invalid_shapes_do_not_write(monkeypatch, rules):
    def unexpected(*args, **kwargs):
        raise AssertionError("uncached shared compiler used for native input")

    data = rdflib_turbo.Dataset()
    before = len(data)
    turbo._compile_native.cache_clear()
    monkeypatch.setattr(shared, "SharedShapes", unexpected)
    invalid = """@prefix sh: <http://www.w3.org/ns/shacl#> .
    <urn:S> a sh:PropertyShape; sh:targetNode <urn:s>; sh:path "literal"; sh:minCount 1."""
    operation = turbo.shacl_rules if rules else turbo.validate
    with pytest.raises(ShapeLoadError, match="Values of a property path cannot be a Literal"):
        operation(data, shacl_graph=invalid, inplace=True)
    assert len(data) == before


def test_public_compile_shapes_still_validates_immediately():
    invalid = """@prefix sh: <http://www.w3.org/ns/shacl#> .
    <urn:S> a sh:PropertyShape; sh:path "literal"; sh:minCount 1."""
    with pytest.raises(ShapeLoadError, match="Values of a property path cannot be a Literal"):
        turbo.compile_shapes(invalid)


def test_standalone_top_level_still_compiles_eagerly(monkeypatch):
    turbo._compile_native.cache_clear()
    native = turbo._native.CompiledShapes
    calls = []

    def compile_native(*args, _policy):
        assert _policy is turbo._native._REGEX_POLICY
        calls.append(args)
        return native.from_input(*args, _policy=_policy)

    monkeypatch.setattr(turbo._native, "CompiledShapes", SimpleNamespace(from_input=compile_native))
    assert not turbo.validate(Graph(), shacl_graph=SHAPES)[0]
    assert len(calls) == 1
