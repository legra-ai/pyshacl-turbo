"""Compare shape discovery and targeting with the reference's inspection API."""

import importlib
import tomllib
from pathlib import Path

import pyshacl_turbo as turbo
import pytest
from pyshacl.shapes_graph import ShapesGraph as ReferenceShapesGraph
from rdflib import RDF, BNode, Dataset, Literal
from test_compatibility import EX, SH, graph


@pytest.mark.parametrize("dataset", [False, True])
def test_shape_discovery_and_focus_nodes_match_reference(dataset):
    shapes = graph("""
        ex:Node a sh:NodeShape; sh:targetNode ex:missing, "literal";
          sh:targetClass ex:Parent; sh:property ex:Property.
        ex:Property sh:path ex:p; sh:targetSubjectsOf ex:p; sh:targetObjectsOf ex:q.
        ex:Implicit a rdfs:Class, sh:NodeShape.
        ex:Off a sh:NodeShape; sh:deactivated true; sh:targetNode ex:off.
    """)
    data = graph("""ex:Child rdfs:subClassOf ex:Parent. ex:a a ex:Child.
        ex:b ex:p 1. ex:c ex:q ex:d. ex:i a ex:Implicit.""")
    blank = BNode("caller-node")
    data.add((blank, RDF.type, EX.Parent))
    if dataset:
        source = Dataset()
        source.graph(EX.named).__iadd__(data)
        data = source
        data.default_union = True
    expected = ReferenceShapesGraph(shapes)
    module = importlib.import_module("pyshacl_turbo.shapes_graph")
    shape_module = importlib.import_module("pyshacl_turbo.shape")
    actual = module.ShapesGraph(shapes)
    assert turbo.ShapesGraph is module.ShapesGraph
    assert turbo.Shape is shape_module.Shape
    expected_shapes = {s.node: s for s in expected.shapes}
    actual_shapes = {s.node: s for s in actual.shapes}
    assert actual_shapes.keys() == expected_shapes.keys()
    for node, reference in expected_shapes.items():
        shape = actual.lookup_shape_from_node(node)
        assert shape is actual_shapes[node]
        assert shape.sg is actual
        assert shape.path() == reference.path()
        assert shape.is_property_shape == reference.is_property_shape
        assert shape.deactivated == reference.deactivated
        assert shape.focus_nodes(data) == reference.focus_nodes(data)
        assert [set(v) for v in shape.target()] == [set(v) for v in reference.target()]
    assert blank in actual_shapes[EX.Node].focus_nodes(data)
    assert Literal("literal") in actual_shapes[EX.Node].focus_nodes(data)
    assert actual.shapes_from_uris([EX.Node])[0] is actual_shapes[EX.Node]
    with pytest.raises(KeyError):
        actual.lookup_shape_from_node(EX.absent)


def test_advanced_sparql_focus_nodes_match_reference():
    shapes = graph("""ex:S a sh:NodeShape; sh:target [a sh:SPARQLTarget;
        sh:select "SELECT ?this WHERE { ?this <https://example.com/p> 3 }"] .""")
    data = graph("ex:s ex:p 3. ex:other ex:p 4.")
    expected = next(iter(ReferenceShapesGraph(shapes).shapes))
    expected.set_advanced(True)
    actual = next(iter(turbo.ShapesGraph(shapes).shapes))
    assert actual.focus_nodes(data) == set()
    actual.set_advanced(True)
    assert actual.focus_nodes(data) == expected.focus_nodes(data) == {EX.s}
    data.add((EX.added, EX.p, Literal(3)))
    assert actual.focus_nodes(data) == expected.focus_nodes(data) == {EX.s, EX.added}
    data.remove((EX.s, EX.p, None))
    assert actual.focus_nodes(data) == expected.focus_nodes(data) == {EX.added}


def test_shape_metadata_graph_access_and_blank_node_identity():
    shapes = graph("""ex:S a sh:NodeShape; sh:name "name"; sh:description "description";
        sh:message "message"; sh:severity sh:Warning; sh:order 2.5;
        sh:property [sh:path ex:p; sh:minCount 1].""")
    expected = ReferenceShapesGraph(shapes)
    actual = turbo.ShapesGraph(shapes)
    expected_shapes = {shape.node: shape for shape in expected.shapes}
    actual_shapes = {shape.node: shape for shape in actual.shapes}
    assert actual_shapes.keys() == expected_shapes.keys()
    assert list(actual.shapes) == list(actual.shapes)
    for node, reference in expected_shapes.items():
        shape = actual_shapes[node]
        for name in ("severity", "order"):
            assert getattr(shape, name) == getattr(reference, name)
        for name in ("message", "name", "description"):
            assert set(getattr(shape, name)) == set(getattr(reference, name))
        assert set(shape.property_shapes()) == set(reference.property_shapes())
        for other in reference.property_shapes():
            assert shape.get_other_shape(other) is actual_shapes[other]
        assert shape.focus_nodes(graph("")) == set()
    for name, args in (
        ("objects", (EX.S, SH.property)),
        ("subjects", (SH.path, EX.p)),
        ("predicates", (EX.S, None)),
        ("predicate_objects", (EX.S,)),
        ("subject_objects", (SH.property,)),
        ("subject_predicates", (EX.p,)),
    ):
        assert set(getattr(actual, name)(*args)) == set(getattr(expected, name)(*args))
    fresh = turbo.ShapesGraph(shapes)
    assert fresh.shapes_from_uris([EX.S])[0].node == EX.S
    dataset = Dataset()
    dataset.graph(EX.named).__iadd__(shapes)
    assert {shape.node for shape in turbo.ShapesGraph(dataset).shapes} == actual_shapes.keys()
    with pytest.raises(TypeError, match="RDFLib"):
        turbo.ShapesGraph("not a graph")


def test_release_metadata_describes_functionality_without_maturity_labels():
    metadata = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
    assert metadata["project"]["description"] == (
        "A Rust SHACL engine with Python bindings and pySHACL-compatible APIs"
    )
    assert not any(
        value.startswith("Development Status ::") for value in metadata["project"]["classifiers"]
    )


def test_prepared_target_data_reuses_snapshot_and_keeps_mutations_explicit(monkeypatch):
    from pyshacl_turbo import target_data

    shapes = turbo.ShapesGraph(graph("ex:S a sh:NodeShape; sh:targetClass ex:Person."))
    shape = next(iter(shapes.shapes))
    source = graph("ex:a a ex:Person.")
    snapshots = []
    original = target_data.input_graph

    def capture(data, **kwargs):
        snapshots.append(data)
        return original(data, **kwargs)

    monkeypatch.setattr(target_data, "input_graph", capture)
    prepared = turbo.prepare_target_data(source)
    assert isinstance(prepared, turbo.TargetData)
    assert turbo.prepare_target_data(prepared) is prepared
    assert shape.focus_nodes(prepared) == {EX.a}
    shape.focus_nodes(prepared).clear()
    assert shape.focus_nodes(prepared) == {EX.a}
    assert len(snapshots) == 1
    source.add((EX.b, RDF.type, EX.Person))
    source.remove((EX.a, RDF.type, EX.Person))
    assert shape.focus_nodes(prepared) == {EX.a}
    assert shape.focus_nodes(source) == {EX.b}
    assert shape.focus_nodes(turbo.prepare_target_data(source)) == {EX.b}


def test_prepared_target_data_separates_shape_programs_and_advanced_modes():
    prepared = turbo.prepare_target_data(graph("ex:a ex:p 3. ex:b ex:p 4."))
    sg = turbo.ShapesGraph(
        graph("""ex:S a sh:NodeShape; sh:targetNode ex:explicit;
        sh:target [a sh:SPARQLTarget;
          sh:select "SELECT ?this WHERE { ?this <https://example.com/p> 3 }"] .
        ex:Other a sh:NodeShape; sh:targetNode ex:other.""")
    )
    shapes = {s.node: s for s in sg.shapes}
    shape = shapes[EX.S]
    assert shape.focus_nodes(prepared) == {EX.explicit}
    shape.set_advanced(True)
    assert shape.focus_nodes(prepared) == {EX.explicit, EX.a}
    shape.set_advanced(False)
    assert shape.focus_nodes(prepared) == {EX.explicit}
    assert shapes[EX.Other].focus_nodes(prepared) == {EX.other}
    other = next(iter(turbo.ShapesGraph(graph("ex:S sh:targetNode ex:different.")).shapes))
    assert other.focus_nodes(prepared) == {EX.different}


@pytest.mark.parametrize("dataset", [False, True])
def test_prepared_target_data_preserves_terms_and_graph_scope(dataset):
    from rdflib.namespace import XSD

    source = graph('ex:s ex:p "3", "3"^^xsd:string; ex:q _:focus.')
    blank = source.value(EX.s, EX.q)
    if dataset:
        quads = Dataset()
        quads.graph(EX.named).__iadd__(source)
        source = quads
    shape = next(
        iter(
            turbo.ShapesGraph(
                graph("""ex:S a sh:NodeShape;
        sh:targetObjectsOf ex:p, ex:q.""")
            ).shapes
        )
    )
    prepared = turbo.prepare_target_data(source)
    assert shape.focus_nodes(prepared) == {Literal("3"), Literal("3", datatype=XSD.string), blank}
    assert shape.focus_nodes(prepared) == shape.focus_nodes(source)


def test_prepared_target_data_keeps_named_graphs_for_advanced_targets():
    data = Dataset()
    data.graph(EX.first).add((EX.a, EX.p, Literal(3)))
    data.graph(EX.second).add((EX.b, EX.p, Literal(3)))
    sg = turbo.ShapesGraph(
        graph("""ex:S a sh:NodeShape; sh:target [a sh:SPARQLTarget;
        sh:select "SELECT ?this WHERE { GRAPH <https://example.com/first> { ?this <https://example.com/p> 3 } }"] .""")
    )
    shape = next(iter(sg.shapes))
    shape.set_advanced(True)
    prepared = turbo.prepare_target_data(data)
    assert shape.focus_nodes(prepared) == {EX.a}
    assert shape.focus_nodes(prepared) == shape.focus_nodes(data)
