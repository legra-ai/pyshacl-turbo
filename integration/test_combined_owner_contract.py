"""Real paired-wheel contracts for the combined native-owner consumer fixes."""

import pyshacl_turbo as turbo
import pytest
import rdflib_turbo
from rdflib import BNode, Graph, Namespace, URIRef

SH = Namespace("http://www.w3.org/ns/shacl#")
SHAPES = """@prefix sh:<http://www.w3.org/ns/shacl#>.
<urn:S> sh:targetNode <urn:data:s>, <urn:shapes:s>; sh:class <urn:Required>.
"""


def forbidden(*args, **kwargs):
    raise AssertionError("standalone compiler must not execute for a native owner")


@pytest.mark.parametrize("scope", ["default", "named", "blank"])
def test_real_native_focus_names_use_data_prefixes_without_standalone_compile(monkeypatch, scope):
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
        patch.setattr(turbo._native, "CompiledShapes", forbidden)
        conforms, report, _ = turbo.validate(data, shacl_graph=shapes, focus_nodes=["ex:s"])
    assert not conforms
    assert set(report.objects(None, SH.focusNode)) == {URIRef("urn:data:s")}
    assert data.store.backend._native is owner
    assert len(data) == 1


def test_top_level_real_native_rules_compile_only_in_owner(monkeypatch):
    data = rdflib_turbo.Dataset().parse(data="<urn:s> <urn:p> <urn:o>.", format="turtle")
    shapes = """@prefix sh:<http://www.w3.org/ns/shacl#>.
    <urn:S> sh:targetNode <urn:s>; sh:rule [a sh:TripleRule;
      sh:subject sh:this; sh:predicate <urn:derived>; sh:object <urn:value>]."""
    owner = data._native
    turbo._compile_native.cache_clear()
    with monkeypatch.context() as patch:
        patch.setattr(turbo._native, "CompiledShapes", forbidden)
        assert turbo.shacl_rules(data, shacl_graph=shapes, inplace=True) is data
    assert data._native is owner
    assert (
        URIRef("urn:s"),
        URIRef("urn:derived"),
        URIRef("urn:value"),
    ) in data.to_rdflib().default_graph
    assert len(data) == 2


def test_public_explicit_compilation_retains_eager_native_check(monkeypatch):
    original = turbo._native.CompiledShapes
    calls = []

    def record(*args):
        calls.append(args)
        return original(*args)

    turbo._compile_native.cache_clear()
    with monkeypatch.context() as patch:
        patch.setattr(turbo._native, "CompiledShapes", record)
        turbo.compile_shapes(SHAPES)
    assert len(calls) == 1
    invalid = '@prefix sh:<http://www.w3.org/ns/shacl#>. <urn:S> sh:path "invalid".'
    with pytest.raises(ValueError):
        turbo.compile_shapes(invalid)


def test_real_native_focus_prefix_is_the_data_mapping_after_explicit_compile():
    data = rdflib_turbo.Graph()
    data.bind("ex", URIRef("urn:data:"))
    data.add((URIRef("urn:data:s"), URIRef("urn:p"), URIRef("urn:o")))
    shapes = Graph().parse(data=SHAPES, format="turtle")
    shapes.bind("ex", URIRef("urn:shapes:"))
    conforms, report, _ = turbo.compile_shapes(shapes).validate(data, focus_nodes=["ex:s"])
    assert not conforms
    assert set(report.objects(None, SH.focusNode)) == {URIRef("urn:data:s")}
