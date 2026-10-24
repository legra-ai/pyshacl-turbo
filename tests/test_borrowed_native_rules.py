"""Rules execute on the same scoped native owner used for validation."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import BNode, Dataset, Literal, URIRef
from rdflib_turbo import StoreDataset

P = URIRef("urn:p")
Q = URIRef("urn:derived")
S = URIRef("urn:s")
HIDDEN = URIRef("urn:hidden")
SHAPES = """@prefix sh:<http://www.w3.org/ns/shacl#>.
<urn:Shape> a sh:NodeShape; sh:targetSubjectsOf <urn:p>;
 sh:class <urn:Missing>; sh:rule <urn:Rule>.
<urn:Rule> a sh:TripleRule; sh:subject sh:this; sh:predicate <urn:derived>;
 sh:object [sh:path <urn:p>].
"""


def source(kind, native):
    dataset = StoreDataset() if native else Dataset()
    dataset.default_union = True
    if kind == "default":
        selected = dataset.default_context
    elif kind == "uri":
        selected = dataset.graph(URIRef("urn:selected"))
    elif kind == "blank":
        selected = dataset.graph(BNode("selected"))
    else:
        selected = dataset
    selected.add((S, P, Literal("present")))
    selected.add((BNode("record"), P, Literal("blank")))
    dataset.graph(HIDDEN).add((URIRef("urn:other"), P, Literal("outside")))
    dataset.graph(URIRef("urn:empty"))
    selected.bind("ex", URIRef("urn:"))
    return dataset, selected


def facts(graph):
    return set(graph.triples((None, None, None)))


def quads(dataset):
    return {
        (s, p, o, getattr(context, "identifier", context))
        for s, p, o, context in dataset.quads((None, None, None, None))
    }


@pytest.mark.parametrize("kind", ["default", "uri", "blank", "dataset"])
@pytest.mark.parametrize("inplace", [False, True])
def test_native_rule_output_matches_original_without_validating_constraints(kind, inplace):
    expected_owner, expected_source = source(kind, False)
    expected_before = quads(expected_owner)
    expected = pyshacl.shacl_rules(
        expected_source, shacl_graph=SHAPES, advanced=True, inplace=inplace
    )
    owner, selected = source(kind, True)
    before = quads(owner)
    result = turbo.shacl_rules(selected, shacl_graph=SHAPES, advanced=True, inplace=inplace)
    assert facts(result) == facts(expected)
    assert quads(owner) == quads(expected_owner)
    assert dict(result.namespaces()) == dict(selected.namespaces())
    if inplace:
        assert result is selected
        assert (S, Q, Literal("present")) in facts(selected)
        if kind != "dataset":
            assert (URIRef("urn:other"), Q, Literal("outside")) not in facts(owner.graph(HIDDEN))
    else:
        assert result is not selected
        assert quads(owner) == before
        assert quads(expected_owner) == expected_before
        result.add((S, URIRef("urn:independent"), Literal(True)))
        assert (S, URIRef("urn:independent"), Literal(True)) not in facts(selected)


@pytest.mark.parametrize("inplace", [False, True])
def test_rules_inside_native_transaction_include_pending_rows_and_keep_the_owner(inplace):
    owner, selected = source("uri", True)
    with selected.transaction() as transaction:
        transaction.add((URIRef("urn:pending"), P, Literal("pending")))
        result = turbo.compile_shapes(SHAPES, advanced=True).shacl_rules(
            transaction, inplace=inplace
        )
        assert (URIRef("urn:pending"), Q, Literal("pending")) in facts(result)
        assert ((S, Q, Literal("present")) in facts(transaction)) is inplace
        assert ((S, Q, Literal("present")) in facts(selected)) is False
    assert ((S, Q, Literal("present")) in facts(selected)) is inplace
    assert len(owner.graph(HIDDEN)) == 1


def test_postprocessing_failure_aborts_pending_rule_writes(monkeypatch):
    owner, selected = source("uri", True)
    before = quads(owner)

    def reject_output(warnings):
        raise ValueError("rule warning processing failed")

    monkeypatch.setattr(turbo, "_emit_recursion_warnings", reject_output)
    with pytest.raises(ValueError, match="rule warning processing failed"):
        turbo.shacl_rules(selected, shacl_graph=SHAPES, advanced=True, inplace=True)
    assert quads(owner) == before
    selected.add((S, URIRef("urn:writer-released"), Literal(True)))
    assert (S, URIRef("urn:writer-released"), Literal(True)) in facts(selected)


def test_committed_noninplace_rules_can_read_while_another_transaction_is_open():
    owner, selected = source("uri", True)
    before = quads(owner)
    with selected.transaction() as transaction:
        transaction.add((URIRef("urn:pending"), P, Literal("pending")))
        result = turbo.shacl_rules(selected, shacl_graph=SHAPES, advanced=True)
        assert (S, Q, Literal("present")) in facts(result)
        assert not list(result.objects(URIRef("urn:pending"), Q))
        assert quads(owner) == before
