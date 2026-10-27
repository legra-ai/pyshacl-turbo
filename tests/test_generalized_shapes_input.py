"""Shapes retain the term domain and context selected by original RDFLib inputs."""

import pytest
from pyshacl import validate as reference_validate
from pyshacl_turbo import CompiledShapes, validate
from rdflib import RDF, BNode, Dataset, Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib_turbo import StoreDataset

SH = Namespace("http://www.w3.org/ns/shacl#")
EX = Namespace("urn:generalized-shapes:")


def shapes(kind, *, literal_shape=True):
    source = Dataset(default_union=kind.endswith("-on"))
    named = source.graph(EX.scope)
    blank = source.graph(BNode("scope"))
    for graph, node, focus in (
        (named, Literal("shape") if literal_shape else EX.first, EX.focus1),
        (blank, EX.second, EX.focus2),
    ):
        graph.add((node, RDF.type, SH.NodeShape))
        graph.add((node, SH.targetNode, focus))
        graph.add((node, SH["class"], EX.Required))
    if kind == "selected-named":
        return named
    if kind == "selected-blank":
        return blank
    return source


def assert_reports_match(source_factory):
    # Reference shape construction has observable bootstrap/union side effects;
    # each implementation receives an independent but equivalent source graph.
    expected = reference_validate(Graph(), shacl_graph=source_factory())
    actual = validate(Graph(), shacl_graph=source_factory())
    assert actual[0] == expected[0]
    assert isomorphic(actual[1], expected[1])


@pytest.mark.parametrize(
    "kind",
    (
        "selected-named",
        "selected-blank",
        "dataset-default-union-off",
        "dataset-default-union-on",
    ),
)
def test_literal_shape_ids_keep_selected_and_union_scope(kind):
    assert_reports_match(lambda: shapes(kind))


@pytest.mark.parametrize("kind", ("dataset-default-union-off", "dataset-default-union-on"))
def test_uri_shape_controls_preserve_existing_dataset_union_behavior(kind):
    assert_reports_match(lambda: shapes(kind, literal_shape=False))


@pytest.mark.parametrize("subject_kind", ("iri", "blank", "literal"))
@pytest.mark.parametrize("predicate_kind", ("iri", "blank", "literal"))
def test_unrelated_shape_metadata_keeps_generalized_subjects_and_predicates(
    subject_kind, predicate_kind
):
    def term(kind, name):
        if kind == "iri":
            return URIRef(EX[name])
        if kind == "blank":
            return BNode(name)
        return Literal(name)

    def fixture():
        graph = shapes("selected-blank")
        graph.add(
            (term(subject_kind, "metadata-s"), term(predicate_kind, "metadata-p"), Literal("value"))
        )
        return graph

    assert_reports_match(fixture)


@pytest.mark.parametrize("identifier", ("urn:shape", "relative-shape"))
def test_typed_shape_iris_preserve_rdflib_lexical_acceptance(identifier):
    def fixture():
        graph = Graph()
        shape = URIRef(identifier)
        prop = BNode("property")
        graph.add((shape, SH.targetNode, EX.focus))
        graph.add((shape, SH.property, prop))
        graph.add((prop, SH.path, EX.required))
        graph.add((prop, SH.minCount, Literal(1)))
        return graph

    expected = reference_validate(Graph(), shacl_graph=fixture())
    actual = validate(Graph(), shacl_graph=fixture())
    assert actual[0] == expected[0] is False
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]


@pytest.mark.parametrize("identifier", ("shape", "", "not a standard blank label"))
def test_typed_blank_shape_identifiers_retain_rdflib_node_values(identifier):
    def fixture():
        graph = Graph()
        shape = BNode(identifier)
        graph.add((shape, SH.targetNode, EX.focus))
        graph.add((shape, SH["class"], EX.Required))
        return graph

    assert_reports_match(fixture)


@pytest.mark.parametrize("scope", ("dataset", None, URIRef(EX.scope), BNode("scope")))
def test_native_shape_sources_pin_their_selected_owner_without_python_traversal(scope, monkeypatch):
    source = StoreDataset()
    graph = (
        source
        if scope == "dataset"
        else source.default_graph
        if scope is None
        else source.graph(scope)
    )
    graph.add((EX.shape, SH.targetNode, EX.focus))
    graph.add((EX.shape, SH["class"], EX.Required))
    hidden = source.graph(EX.hidden)
    hidden.add((EX.hidden_shape, SH.targetNode, EX.other))
    hidden.add((EX.hidden_shape, SH["class"], EX.Required))
    expected_shapes = Graph()
    expected_shapes.add((EX.shape, SH.targetNode, EX.focus))
    expected_shapes.add((EX.shape, SH["class"], EX.Required))
    if scope == "dataset":
        expected_shapes.add((EX.hidden_shape, SH.targetNode, EX.other))
        expected_shapes.add((EX.hidden_shape, SH["class"], EX.Required))
    data = Graph()
    data.add((EX.focus, RDF.type, EX.Required))
    expected = reference_validate(data, shacl_graph=expected_shapes)

    def forbid(*args, **kwargs):
        raise AssertionError("Native shape compilation traversed or serialized its Python graph")

    with monkeypatch.context() as context:
        context.setattr(graph.store, "triples", forbid)
        context.setattr(graph, "serialize", forbid)
        compiled = CompiledShapes(graph)
    graph.set((EX.shape, SH["class"], EX.Later))
    source.close()
    actual = compiled.validate(data)
    assert actual[0] == expected[0] == (scope != "dataset")
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]


def test_pending_native_shape_compilation_does_not_escape_an_unowned_transaction():
    source = StoreDataset()
    with pytest.raises(NotImplementedError, match="pending"), source.transaction() as transaction:
        transaction.default_graph.add((EX.shape, SH.targetNode, EX.focus))
        CompiledShapes(transaction.default_graph)
    assert len(source) == 0
    source.close()
