"""Exact paired wheels expand rules without crossing the dataset boundary."""

import pyshacl_turbo as turbo
import pytest
from rdflib import Dataset as RDFDataset
from rdflib import Graph, URIRef
from rdflib_turbo import Dataset

SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <urn:example:> .
ex:S sh:targetSubjectsOf ex:p; sh:rule [a sh:TripleRule;
  sh:subject sh:this; sh:predicate ex:derived; sh:object [sh:path ex:p]].
"""
SOURCE = """@prefix ex: <urn:example:> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
ex:g { _:focus ex:p "01"^^xsd:integer, "word", "word"^^xsd:string. }
"""


def quads(graph):
    if isinstance(graph, RDFDataset):
        return set(graph.quads())
    return {(s, p, o, URIRef("urn:x-rdflib:default")) for s, p, o in graph}


@pytest.mark.parametrize("inplace", [False, True])
def test_compiled_native_rules_preserve_exact_quads_and_namespace_bindings(monkeypatch, inplace):
    data = Dataset().parse(data=SOURCE, format="trig")
    original = data._native
    before = quads(data.to_rdflib())
    bindings = dict(data.namespaces())
    program = turbo.compile_shapes(Graph().parse(data=SHAPES, format="turtle"), advanced=True)
    expected = quads(program.shacl_rules(data.to_rdflib()))

    def forbidden(*args, **kwargs):
        raise AssertionError("shared rules must not copy, serialize or convert native input")

    with monkeypatch.context() as patch:
        for name in ("to_rdflib", "from_rdflib", "serialize", "copy"):
            patch.setattr(Dataset, name, forbidden)
        patch.setattr(turbo, "_input", forbidden)
        result = program.shacl_rules(data, inplace=inplace)
    assert (result is data) is inplace
    assert data._native is original
    assert quads(result.to_rdflib()) == expected
    assert dict(result.namespaces()) == bindings
    assert quads(data.to_rdflib()) == (expected if inplace else before)
    assert {quad for quad in expected if quad[3] == URIRef("urn:example:g")} == before
    assert len(expected - before) == 3


def test_public_native_rules_keep_original_on_iteration_failure():
    data = Dataset().parse(data=SOURCE, format="trig")
    before = quads(data.to_rdflib())
    with pytest.raises(ValueError, match="iteration"):
        turbo.shacl_rules(
            data, shacl_graph=SHAPES, inplace=True, iterate_rules=True, max_rule_iterations=0
        )
    assert quads(data.to_rdflib()) == before
