"""Inference, SHACL rules and callbacks share one private acceptance boundary."""

import warnings
from contextlib import nullcontext

import pyshacl_turbo as turbo
import pytest
from pyshacl import validate as reference_validate
from rdflib import Graph
from rdflib.compare import isomorphic
from rdflib_turbo import Dataset, Store
from rdflib_turbo import Graph as NativeGraph

DATA = "<urn:a> <urn:child> <urn:b>. <urn:child> <http://www.w3.org/2000/01/rdf-schema#subPropertyOf> <urn:parent>."
RULE = """@prefix sh:<http://www.w3.org/ns/shacl#>.
<urn:S> sh:targetSubjectsOf <urn:parent>;
 sh:rule [a sh:TripleRule;sh:subject sh:this;sh:predicate <urn:name>;sh:object "derived"];
 sh:property [sh:path <urn:name>;sh:minCount 1]."""
RECURSIVE = """@prefix sh:<http://www.w3.org/ns/shacl#>.
<urn:S> sh:targetNode <urn:a>;sh:rule <urn:R>.
<urn:R> a sh:TripleRule;sh:condition <urn:C>;
 sh:subject sh:this;sh:predicate <urn:derived>;sh:object true.
<urn:C> sh:node <urn:C>."""


def managed(factory):
    source = factory()
    return source if hasattr(source, "__enter__") else nullcontext(source)


@pytest.mark.parametrize("factory", [Store, Dataset, NativeGraph])
@pytest.mark.parametrize("mode", ["rdfs", "owlrl", "both"])
@pytest.mark.parametrize("inplace", [False, True])
def test_rules_and_constraints_see_the_same_private_inference(factory, mode, inplace):
    shapes = Graph().parse(data=RULE, format="turtle")
    expected = reference_validate(
        Graph().parse(data=DATA, format="turtle"),
        shacl_graph=shapes,
        inference=mode,
        advanced=True,
        inplace=inplace,
    )
    with managed(factory) as source:
        source.parse(data=DATA)
        before = source.serialize()
        actual = turbo.validate(
            source, shacl_graph=shapes, inference=mode, advanced=True, inplace=inplace
        )
        assert actual[0] == expected[0] is True
        assert isomorphic(actual[1], expected[1])
        assert bool(source.query('ASK {<urn:a> <urn:name> "derived"}')) == inplace
        if not inplace:
            assert source.serialize() == before


@pytest.mark.parametrize("factory", [Store, Dataset, NativeGraph])
def test_warning_as_error_discards_both_inference_and_rule_output(factory):
    shapes = Graph().parse(data=RECURSIVE, format="turtle")
    with managed(factory) as source:
        source.parse(data=DATA)
        before = source.serialize()
        namespaces = tuple(source.namespaces()) if hasattr(source, "namespaces") else None
        with warnings.catch_warnings():
            warnings.simplefilter("error", turbo.ShapeRecursionWarning)
            with pytest.raises(turbo.ShapeRecursionWarning, match="Recursive Shape"):
                turbo.validate(
                    source, shacl_graph=shapes, inference="rdfs", advanced=True, inplace=True
                )
        assert source.serialize() == before
        if namespaces is not None:
            assert tuple(source.namespaces()) == namespaces


def test_reentrant_transaction_mutation_conflicts_and_aborts_prior_pending_writes(monkeypatch):
    shapes = Graph().parse(data=RECURSIVE, format="turtle")
    with Store() as source:
        with (
            pytest.raises(RuntimeError, match="Transaction changed"),
            source.transaction() as pending,
        ):
            pending.parse(data=DATA)
            observed = []

            def mutate(*args, **kwargs):
                observed.append(len(pending))
                assert not pending.query("ASK {<urn:a> <urn:parent> <urn:b>}", default_union=True)
                pending.parse(data="")

            monkeypatch.setattr(warnings, "showwarning", mutate)
            with warnings.catch_warnings():
                warnings.simplefilter("always", turbo.ShapeRecursionWarning)
                turbo.validate(
                    pending, shacl_graph=shapes, inference="rdfs", advanced=True, inplace=True
                )
        assert observed == [2]
        assert len(source) == 0


@pytest.mark.parametrize("factory", [Store, Dataset, NativeGraph])
@pytest.mark.parametrize("mode", ["rdfs", "owlrl", "both"])
@pytest.mark.parametrize("function", [False, True])
def test_native_sparql_constraints_and_functions_read_private_entailments(factory, mode, function):
    query = "SELECT $this WHERE {$this <urn:parent> <urn:b>}"
    declaration = ""
    if function:
        declaration = """<urn:hasParent> a sh:SPARQLFunction;
          sh:parameter [sh:path <urn:fn#arg>];
          sh:ask 'ASK {$arg <urn:parent> <urn:b>}'."""
        query = "SELECT $this WHERE {FILTER(<urn:hasParent>($this))}"
    shapes = Graph().parse(
        data=f"""@prefix sh:<http://www.w3.org/ns/shacl#>.
    {declaration}
    <urn:S> sh:targetSubjectsOf <urn:parent>;sh:sparql [
      sh:message "derived parent edge";sh:select "{query}"].""",
        format="turtle",
    )
    reference = Graph().parse(data=DATA, format="turtle")
    assert reference_validate(reference, shacl_graph=shapes, advanced=True)[0]
    expected = reference_validate(reference, shacl_graph=shapes, inference=mode, advanced=True)
    with managed(factory) as source:
        source.parse(data=DATA)
        actual = turbo.validate(source, shacl_graph=shapes, inference=mode, advanced=True)
        assert actual[0] == expected[0] is False
        assert isomorphic(actual[1], expected[1])
