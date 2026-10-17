"""Cross-wheel contract tests; CI installs the exact companion runtime wheel."""

import pytest
from owlrl_turbo import expand
from pyshacl import validate as reference_validate
from pyshacl_turbo import compile_shapes, validate
from rdflib import BNode, Graph, URIRef
from rdflib.compare import isomorphic
from rdflib_turbo import Dataset

DATA = """@prefix ex: <urn:example:> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
ex:Employee rdfs:subClassOf ex:Person. ex:s a ex:Employee.
"""
SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <urn:example:> .
ex:S sh:targetClass ex:Person; sh:property ex:P.
ex:P sh:path ex:name; sh:minCount 1.
"""


def test_three_products_use_one_dataset_and_complete_reference_report(monkeypatch):
    data = Dataset().parse(data=DATA)
    identity = data._native
    expand(data, inference="rdfs", inplace=True)
    expected = reference_validate(data.to_rdflib().default_graph, shacl_graph=SHAPES)
    shape_graph = Graph().parse(data=SHAPES, format="turtle")
    program = compile_shapes(shape_graph)

    def forbidden(*args, **kwargs):
        raise AssertionError("shared validation must not copy, serialize or convert its dataset")

    with monkeypatch.context() as patch:
        for name in ("to_rdflib", "from_rdflib", "serialize", "copy"):
            patch.setattr(Dataset, name, forbidden)
        actual = program.validate(data)
        repeated = validate(data, shacl_graph=shape_graph)
    assert data._native is identity
    for result in (actual, repeated):
        assert result[0] == expected[0]
        assert isomorphic(result[1], expected[1])
        assert result[2] == expected[2]
    data.parse(data='@prefix ex: <urn:example:> . ex:s ex:name "Name".')
    assert program.validate(data)[0]


def test_named_graph_and_blank_node_identity_survive_validation():
    data = Dataset().parse(
        data='<urn:g> { _:focus <urn:p> "01"^^<http://www.w3.org/2001/XMLSchema#integer>. }',
        format="trig",
    )
    before = data.serialize()
    source = data.to_rdflib()
    focus = next(source.quads())[0]
    shapes = Graph().parse(
        data="@prefix sh: <http://www.w3.org/ns/shacl#> . <urn:S> sh:targetSubjectsOf <urn:p>; sh:class <urn:C>.",
        format="turtle",
    )
    result = validate(data, shacl_graph=shapes)
    assert not result[0]
    assert isinstance(focus, BNode)
    assert (None, URIRef("http://www.w3.org/ns/shacl#focusNode"), focus) in result[1]
    assert data.serialize() == before


def test_native_input_rejects_unsupported_conversion_options():
    data = Dataset().parse(data=DATA)
    with pytest.raises(NotImplementedError, match="owlrl-turbo"):
        validate(data, shacl_graph=SHAPES, inference="rdfs")
    with pytest.raises(ValueError, match="data_graph_format"):
        validate(data, shacl_graph=SHAPES, data_graph_format="turtle")


def test_shared_shapes_keep_document_and_graph_boolean_policies(tmp_path):
    shapes = """@prefix sh: <http://www.w3.org/ns/shacl#> .
    <urn:S> sh:targetNode <urn:s>; sh:path <urn:p>;
    sh:uniqueLang "1"^^<http://www.w3.org/2001/XMLSchema#boolean>."""
    path = tmp_path / "shapes.ttl"
    path.write_text(shapes)
    source = '<urn:s> <urn:p> "one"@en, "two"@en.'
    data = Dataset().parse(data=source)
    for argument in (str(path), Graph().parse(data=shapes, format="turtle")):
        assert (
            validate(data, shacl_graph=argument)[0]
            == reference_validate(
                Graph().parse(data=source, format="turtle"), shacl_graph=argument
            )[0]
        )
