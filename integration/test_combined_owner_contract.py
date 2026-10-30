"""Real paired-wheel contracts for the combined native-owner consumer fixes."""

from types import SimpleNamespace

import pyshacl_turbo as turbo
import pytest
import rdflib_turbo
from rdflib import BNode, Graph, Namespace, URIRef

SH = Namespace("http://www.w3.org/ns/shacl#")
SHAPES = """@prefix sh:<http://www.w3.org/ns/shacl#>.
<urn:S> sh:targetNode <urn:data:s>, <urn:shapes:s>; sh:class <urn:Required>.
"""


@pytest.fixture
def compiled(monkeypatch):
    constructor = turbo._native.CompiledShapes
    shared_type = rdflib_turbo._native.SharedShapes
    calls, borrowed = [], []

    def record(*args, **kwargs):
        result = constructor.from_input(*args, **kwargs)
        calls.append(result)
        return result

    class Shared:
        def __new__(cls, *args, **kwargs):
            raise AssertionError("shared consumer must borrow the compiled owner")

        @staticmethod
        def from_compiled(program, *, _comparison_policy):
            assert program in calls
            result = shared_type.from_compiled(program, _comparison_policy=_comparison_policy)
            assert result.shares_program(program)
            borrowed.append(program)
            return result

    turbo._compile_native.cache_clear()
    monkeypatch.setattr(turbo._native, "CompiledShapes", SimpleNamespace(from_input=record))
    monkeypatch.setattr(rdflib_turbo._native, "SharedShapes", Shared)
    yield SimpleNamespace(programs=calls, borrowed=borrowed)
    turbo._compile_native.cache_clear()


def forbidden(*args, **kwargs):
    raise AssertionError("native DATA must not be copied, serialized or converted")


@pytest.mark.parametrize("scope", ["default", "named", "blank"])
def test_real_native_focus_names_use_data_prefixes_with_one_compiled_owner(
    monkeypatch, compiled, scope
):
    dataset = rdflib_turbo.StoreDataset()
    identifier = URIRef("urn:g") if scope == "named" else BNode("g")
    data = dataset.default_graph if scope == "default" else dataset.graph(identifier)
    data.bind("ex", URIRef("urn:data:"))
    data.add((URIRef("urn:data:s"), URIRef("urn:p"), URIRef("urn:o")))
    shapes = Graph().parse(data=SHAPES, format="turtle")
    shapes.bind("ex", URIRef("urn:shapes:"))
    owner = data.store.backend._native
    turbo._compile_native.cache_clear()
    with monkeypatch.context() as patch:
        for name in ("__iter__", "triples", "serialize"):
            patch.setattr(type(data), name, forbidden)
        patch.setattr(turbo, "_input", forbidden)
        conforms, report, _ = turbo.validate(data, shacl_graph=shapes, focus_nodes=["ex:s"])
    assert not conforms
    assert set(report.objects(None, SH.focusNode)) == {URIRef("urn:data:s")}
    assert data.store.backend._native is owner
    assert len(data) == 1
    assert len(compiled.programs) == 1
    assert compiled.borrowed == compiled.programs


def test_top_level_real_native_rules_reuse_one_compiled_owner(monkeypatch, compiled):
    data = rdflib_turbo.Dataset().parse(data="<urn:s> <urn:p> <urn:o>.", format="turtle")
    shapes = """@prefix sh:<http://www.w3.org/ns/shacl#>.
    <urn:S> sh:targetNode <urn:s>; sh:rule [a sh:TripleRule;
      sh:subject sh:this; sh:predicate <urn:derived>; sh:object <urn:value>]."""
    owner = data.store.backend._native
    turbo._compile_native.cache_clear()
    with monkeypatch.context() as patch:
        patch.setattr(type(data), "serialize", forbidden)
        patch.setattr(type(data), "to_rdflib", forbidden)
        patch.setattr(turbo, "_input", forbidden)
        assert turbo.shacl_rules(data, shacl_graph=shapes, inplace=True) is data
    assert data.store.backend._native is owner
    assert len(compiled.programs) == 1
    assert compiled.borrowed == compiled.programs
    assert (
        URIRef("urn:s"),
        URIRef("urn:derived"),
        URIRef("urn:value"),
    ) in data.to_rdflib().default_graph
    assert len(data) == 2


def test_public_explicit_compilation_retains_eager_native_check(compiled):
    turbo.compile_shapes(SHAPES)
    assert len(compiled.programs) == 1
    assert compiled.borrowed == []
    invalid = (
        '@prefix sh:<http://www.w3.org/ns/shacl#>. '
        '<urn:S> a sh:PropertyShape; sh:path "invalid".'
    )
    with pytest.raises(turbo.ShapeLoadError) as failure:
        turbo.compile_shapes(invalid)
    assert failure.value.args == [
        "Values of a property path cannot be a Literal.",
        "https://www.w3.org/TR/shacl/#property-paths",
    ]


def test_real_native_focus_prefix_is_the_data_mapping_after_explicit_compile():
    data = rdflib_turbo.Graph()
    data.bind("ex", URIRef("urn:data:"))
    data.add((URIRef("urn:data:s"), URIRef("urn:p"), URIRef("urn:o")))
    shapes = Graph().parse(data=SHAPES, format="turtle")
    shapes.bind("ex", URIRef("urn:shapes:"))
    conforms, report, _ = turbo.compile_shapes(shapes).validate(data, focus_nodes=["ex:s"])
    assert not conforms
    assert set(report.objects(None, SH.focusNode)) == {URIRef("urn:data:s")}
