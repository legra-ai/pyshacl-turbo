"""Rule commits decode additions only and preserve the caller's RDF terms."""

import pyshacl_turbo as turbo
import pytest
from pyshacl_turbo import rdf
from rdflib import BNode, Dataset, Graph, Literal
from rdflib.namespace import XSD
from test_compatibility import EX, graph


def test_rdflib_commit_without_snapshot_merges_complete_output():
    data = graph('ex:s ex:existing "keep".')
    rdf.commit_serialized(data, f'<{EX.s}> <{EX.added}> "new" .')
    assert set(data) == {
        (EX.s, EX.existing, Literal("keep")),
        (EX.s, EX.added, Literal("new")),
    }


@pytest.mark.parametrize("dataset", [False, True])
def test_rdflib_commit_decodes_only_added_quads(dataset, monkeypatch):
    data = Dataset(default_union=True) if dataset else Graph()
    context = BNode("context")
    destination = data.graph(context) if dataset else data
    node = BNode("subject")
    lexical = Literal("01", datatype=XSD.integer, normalize=False)
    destination.add((node, EX.existing, lexical))
    snapshot = rdf.input_graph(data)
    suffix = f" {context.n3()}" if dataset else ""
    addition = f'{node.n3()} <{EX.added}> "ok"^^<{XSD.string}>{suffix} .\n'
    expanded = snapshot.source + "\n" + addition
    original_decode = rdf.decode
    decoded = []

    def decode_delta(source, *args, **kwargs):
        result = original_decode(source, *args, **kwargs)
        decoded.append(result)
        assert len(result) == 1
        assert (node, EX.existing, lexical) not in result
        return result

    monkeypatch.setattr(rdf, "decode", decode_delta)
    # A delta commit must not restore an input triple deleted after the snapshot.
    destination.remove((node, EX.existing, lexical))
    rdf.commit_serialized(data, expanded, snapshot.blank_nodes, before=snapshot)
    assert len(decoded) == 1
    assert set(destination) == {(node, EX.added, Literal("ok", datatype=XSD.string))}
    if dataset:
        assert not data.default_graph


@pytest.mark.parametrize("dataset", [False, True])
def test_inplace_rules_return_original_graph_without_materializing_full_output(
    dataset, monkeypatch
):
    data = Dataset(default_union=True) if dataset else Graph()
    data.bind("ex", EX)
    destination = data.graph(EX.named) if dataset else data
    node = BNode("subject")
    lexical = Literal("01", datatype=XSD.integer, normalize=False)
    destination.add((node, EX.value, lexical))
    compiled = turbo.compile_shapes(
        graph("""ex:S sh:targetSubjectsOf ex:value; sh:rule [a sh:SPARQLRule;
          sh:construct "CONSTRUCT { $this ex:derived ?v } WHERE { $this ex:value ?v }"]."""),
        advanced=True,
    )

    def unused_output(*args, **kwargs):
        pytest.fail("inplace rules must not decode a discarded expanded graph")

    monkeypatch.setattr(turbo, "_graph", unused_output)
    result = compiled.shacl_rules(data, inplace=True)
    assert result is data
    assert (node, EX.derived, lexical) in data
    assert (node, EX.value, lexical) in destination
    assert str(next(data.objects(node, EX.derived))) == "01"
    assert str(dict(data.namespaces())["ex"]) == str(EX)
