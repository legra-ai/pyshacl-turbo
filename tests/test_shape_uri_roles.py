"""Programmatic URIRef role values retain original RDFLib lexical identity."""

from itertools import permutations

import pytest
from pyshacl import validate as reference_validate
from pyshacl_turbo import validate
from rdflib import BNode, Graph, Literal, Namespace, URIRef

SH = Namespace("http://www.w3.org/ns/shacl#")
SHAPE = URIRef("urn:shape")
FOCUS = URIRef("urn:focus")
LEXICALS = ("", "relative", "relative/path", "not a standard IRI", "urn:absolute")


def same_report_graph(actual, expected):
    # RDFLib's canonicalizer calls URIRef.n3(), which rejects lexical values
    # accepted by these original programmatic inputs. Compare every exact term
    # under a blank-node bijection instead, without serializing or normalizing.
    left = set(actual)
    right = set(expected)
    left_blank = {term for row in left for term in row if isinstance(term, BNode)}
    right_blank = {term for row in right for term in row if isinstance(term, BNode)}
    assert max(len(left_blank), len(right_blank)) <= 4  # bounded: tiny report fixtures
    if len(left) != len(right) or len(left_blank) != len(right_blank):
        return False
    for order in permutations(right_blank):
        mapping = dict(zip(left_blank, order, strict=True))
        if {tuple(mapping.get(term, term) for term in row) for row in left} == right:
            return True
    return False


def test_report_comparator_preserves_unserializable_uri_identity():
    left = Graph().add((BNode("left"), SH.resultPath, URIRef("not a standard IRI")))
    same = Graph().add((BNode("right"), SH.resultPath, URIRef("not a standard IRI")))
    changed = Graph().add((BNode("right"), SH.resultPath, URIRef("another invalid IRI")))
    assert same_report_graph(left, same)
    assert not same_report_graph(left, changed)


def shapes_for(role, lexical, *, matching_datatype=False):
    graph = Graph()
    value = URIRef(lexical)
    if role == "target-class":
        graph.add((SHAPE, SH.targetClass, value))
        graph.add((SHAPE, SH["class"], URIRef("urn:Required")))
    elif role == "datatype":
        target = (
            Literal("value", datatype=value, normalize=False)
            if matching_datatype
            else Literal("value")
        )
        graph.add((SHAPE, SH.targetNode, target))
        graph.add((SHAPE, SH.datatype, value))
    else:
        graph.add((SHAPE, SH.targetNode, FOCUS))
        if role == "path":
            graph.add((SHAPE, SH.path, value))
            graph.add((SHAPE, SH.minCount, Literal(1)))
        else:
            graph.add((SHAPE, SH["class"], value))
    return graph


def assert_original_report(role, lexical, *, matching_datatype=False):
    # Keep unusual lexical terms exclusively in shapes. Ordinary data ingress
    # and serialized parsing have independent contracts and stay unchanged.
    expected = reference_validate(
        Graph(), shacl_graph=shapes_for(role, lexical, matching_datatype=matching_datatype)
    )
    actual = validate(
        Graph(), shacl_graph=shapes_for(role, lexical, matching_datatype=matching_datatype)
    )
    assert actual[0] == expected[0]
    assert same_report_graph(actual[1], expected[1])
    assert actual[2] == expected[2]


@pytest.mark.parametrize("role", ("path", "class", "target-class", "datatype"))
@pytest.mark.parametrize("lexical", LEXICALS)
def test_shape_named_roles_preserve_programmatic_uri_lexicals(role, lexical):
    assert_original_report(role, lexical)


@pytest.mark.parametrize("lexical", LEXICALS)
def test_matching_typed_shape_targets_keep_their_declared_datatype_lexical(lexical):
    assert_original_report("datatype", lexical, matching_datatype=True)


def test_shape_transfer_retains_an_explicit_empty_datatype():
    from pyshacl_turbo.rdf import shape_batches

    batches = list(shape_batches(shapes_for("datatype", "", matching_datatype=True), {}))
    records = [record for terms, _ in batches for record in terms]
    assert (2, "value", "", None) in records


def test_ordinary_data_transfer_keeps_its_existing_empty_datatype_policy():
    from pyshacl_turbo.term_input import _TermBatch

    batch = _TermBatch({})
    batch.append(FOCUS, URIRef("urn:predicate"), Literal("value", datatype=URIRef("")))
    assert batch.records[batch.quads[0][2]] == (2, "value", None, None)


def test_empty_blank_path_keeps_graph_identity_and_original_text_truthiness():
    def fixture():
        graph = Graph()
        path = BNode("")
        graph.add((SHAPE, SH.targetNode, FOCUS))
        graph.add((SHAPE, SH.path, path))
        graph.add((SHAPE, SH.minCount, Literal(1)))
        graph.add((path, SH.inversePath, URIRef("urn:predicate")))
        return graph

    expected = reference_validate(Graph(), shacl_graph=fixture())
    actual = validate(Graph(), shacl_graph=fixture())
    assert actual[0] == expected[0] is False
    assert same_report_graph(actual[1], expected[1])
    assert actual[2] == expected[2]
