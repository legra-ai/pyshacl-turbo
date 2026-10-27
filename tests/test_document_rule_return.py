"""Document rules retain the original owned dataset view and graph scopes."""

from collections import defaultdict
from io import BytesIO, StringIO, TextIOWrapper

import pyshacl
import pyshacl_turbo as turbo
import pytest
from pyshacl_turbo.graph_abstraction import DataGraph, RdfLibDataGraph
from rdflib import BNode, Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SH

EX = Namespace("urn:rule-return:")
PREFIXES = "@prefix ex: <urn:rule-return:> . "


def shapes():
    graph = Graph()
    graph.bind("ex", EX)
    graph.add((EX.shape, SH.targetNode, EX.focus))
    graph.add((EX.shape, SH.rule, EX.rule))
    graph.add((EX.rule, RDF.type, SH.TripleRule))
    graph.add((EX.rule, SH.subject, SH.this))
    graph.add((EX.rule, SH.predicate, EX.derived))
    graph.add((EX.rule, SH.object, EX.value))
    return graph


def term_identity(term):
    if isinstance(term, Literal):
        return "literal", str(term), str(term.datatype or ""), term.language or ""
    return type(term).__name__, str(term), "", ""


def quad_groups(graph):
    # Bounded: these fixtures contain fewer than twenty input and derived rows.
    groups = defaultdict(list)
    for s, p, o, name in graph.quads((None, None, None, None)):
        groups[name].append(tuple(term_identity(term) for term in (s, p, o)))
    result = []
    for name, rows in groups.items():
        if name == graph.default_graph.identifier:
            kind, label = "default", ""
        elif isinstance(name, BNode):
            kind, label = "blank", ""
        else:
            assert isinstance(name, URIRef)
            kind, label = "iri", str(name)
        result.append((kind, label, tuple(sorted(rows))))
    return sorted(result)


def document_source(kind, document, tmp_path):
    if kind == "text":
        return document
    if kind == "bytes":
        return document.encode()
    if kind == "text-stream":
        return TextIOWrapper(BytesIO(document.encode()), encoding="utf-8")
    if kind == "byte-stream":
        return BytesIO(document.encode())
    path = tmp_path / "input.ttl"
    path.write_text(document)
    return str(path)


@pytest.mark.parametrize(
    "source_kind", ("text", "bytes", "text-stream", "byte-stream", "file-name")
)
@pytest.mark.parametrize("inplace", (False, True))
def test_public_document_rules_return_original_dataset_view(source_kind, inplace, tmp_path):
    document = PREFIXES + 'ex:focus ex:plain "plain"; ex:label "word"@en .'
    expected = pyshacl.shacl_rules(
        document_source(source_kind, document, tmp_path),
        shacl_graph=shapes(),
        data_graph_format="turtle",
        inplace=inplace,
    )
    actual = turbo.shacl_rules(
        document_source(source_kind, document, tmp_path),
        shacl_graph=shapes(),
        data_graph_format="turtle",
        inplace=inplace,
    )
    assert type(actual) is RdfLibDataGraph
    assert type(actual).__name__ == type(expected).__name__
    assert actual.context_aware is expected.context_aware is True
    assert actual.is_multigraph() is expected.is_multigraph() is True
    assert actual.default_union is expected.default_union
    assert actual.identifier == expected.identifier == "RDFLibDataset"
    assert quad_groups(actual) == quad_groups(expected)
    assert dict(actual.namespaces()) == dict(expected.namespaces())
    assert (EX.focus, EX.derived, EX.value) in actual.default_graph
    actual.add((EX.focus, EX.changed, Literal("new")))
    assert (EX.focus, EX.changed, Literal("new")) in actual.default_graph
    assert actual.store is actual.impl.store
    assert actual.namespace_manager is actual.impl.namespace_manager


def test_named_and_blank_document_scopes_survive_public_view():
    document = (
        PREFIXES
        + "ex:focus ex:p ex:default . "
        + "ex:named { ex:focus ex:p ex:namedValue . } "
        + "_:blank { ex:focus ex:p ex:blankValue . }"
    )
    expected = pyshacl.shacl_rules(document, shacl_graph=shapes(), data_graph_format="trig")
    actual = turbo.shacl_rules(document, shacl_graph=shapes(), data_graph_format="trig")
    assert type(actual) is RdfLibDataGraph
    assert quad_groups(actual) == quad_groups(expected)
    assert any(isinstance(context.identifier, BNode) for context in actual.graphs())
    assert (EX.focus, EX.p, EX.namedValue) in actual.get_context(EX.named)
    assert (EX.focus, EX.p, EX.default) in actual.default_graph


def test_public_document_view_borrows_the_final_decoded_dataset(monkeypatch):
    decoded = []
    original = turbo._graph

    def capture_final_decode(*args, **kwargs):
        result = original(*args, **kwargs)
        decoded.append(result)
        return result

    monkeypatch.setattr(turbo, "_graph", capture_final_decode)
    result = turbo.shacl_rules(
        PREFIXES + "ex:focus ex:p ex:o .", shacl_graph=shapes(), data_graph_format="turtle"
    )
    assert type(result) is RdfLibDataGraph
    assert len(decoded) == 1
    assert isinstance(decoded[0], Dataset)
    assert result.impl is decoded[0]
    assert result.store is decoded[0].store


@pytest.mark.parametrize("empty", (False, True))
def test_direct_compiled_rules_keep_explicit_graph_result(empty):
    result = turbo.CompiledShapes(Graph()).shacl_rules(
        b"" if empty else b"<urn:s> <urn:p> <urn:o> .", data_graph_format="nt"
    )
    assert type(result) is Graph
    assert not isinstance(result, DataGraph)
    assert len(result) == (0 if empty else 1)


@pytest.mark.parametrize("rdf_format", ("trig", "nquads"))
def test_serialized_document_rules_keep_default_scope(rdf_format):
    source = PREFIXES + "ex:focus ex:p ex:o ."
    options = {
        "shacl_graph": shapes(),
        "data_graph_format": "turtle",
        "serialize_expanded_graph": True,
        "serialize_expanded_graph_format": rdf_format,
    }
    expected = pyshacl.shacl_rules(source, **options)
    options["shacl_graph"] = shapes()
    actual = turbo.shacl_rules(source, **options)
    expected_graph = Dataset(default_union=True).parse(data=expected, format=rdf_format)
    actual_graph = Dataset(default_union=True).parse(data=actual, format=rdf_format)
    assert quad_groups(actual_graph) == quad_groups(expected_graph)


@pytest.mark.parametrize("declare_builtin", (False, True))
def test_core_namespaces_retain_explicit_builtin_prefix_declarations(declare_builtin):
    declaration = (
        "@prefix brick: <https://brickschema.org/schema/Brick#> . " if declare_builtin else ""
    )
    document = PREFIXES + declaration + "ex:focus ex:p ex:o ."
    expected = pyshacl.shacl_rules(document, data_graph_format="turtle", shacl_graph=shapes())
    actual = turbo.shacl_rules(document, data_graph_format="turtle", shacl_graph=shapes())
    bindings = dict(actual.namespaces())
    assert bindings == dict(expected.namespaces())
    assert ("brick" in bindings) is declare_builtin
    assert "schema" not in bindings


@pytest.mark.parametrize("source_kind", ("stringio", "path-object"))
def test_extra_document_sources_reuse_the_same_owned_result_contract(source_kind, tmp_path):
    document = PREFIXES + "ex:focus ex:p ex:o ."
    if source_kind == "stringio":
        source = StringIO(document)
    else:
        source = tmp_path / "extra.ttl"
        source.write_text(document)
    expected = pyshacl.shacl_rules(
        document.encode(), data_graph_format="turtle", shacl_graph=shapes()
    )
    actual = turbo.shacl_rules(source, data_graph_format="turtle", shacl_graph=shapes())
    assert type(actual) is RdfLibDataGraph
    assert quad_groups(actual) == quad_groups(expected)


def test_empty_document_still_returns_an_owned_dataset():
    expected = pyshacl.shacl_rules(PREFIXES, shacl_graph=Graph(), data_graph_format="turtle")
    actual = turbo.shacl_rules(PREFIXES, shacl_graph=Graph(), data_graph_format="turtle")
    assert type(actual) is RdfLibDataGraph
    assert actual.is_multigraph() is expected.is_multigraph() is True
    assert quad_groups(actual) == quad_groups(expected) == []
    assert dict(actual.namespaces()) == dict(expected.namespaces())
    actual.add((EX.focus, EX.p, EX.value))
    assert (EX.focus, EX.p, EX.value) in actual.default_graph
