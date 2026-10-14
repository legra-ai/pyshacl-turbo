"""Public reverse targeting must agree with the reference shape inspection API."""

from pathlib import Path

import pyshacl_turbo as turbo
import pytest
from pyshacl.shapes_graph import ShapesGraph as ReferenceShapesGraph
from pyshacl.target import apply_target_types, gather_target_types
from rdflib import RDF, BNode, Dataset, Literal
from test_compatibility import EX, graph


def reference_targeting(shapes, data, node, skip=()):
    found = []
    graph = ReferenceShapesGraph(shapes)
    apply_target_types(gather_target_types(graph))
    for shape in graph.shapes:
        if shape.is_property_shape or shape.deactivated or shape.node in skip:
            continue
        shape.set_advanced(True)
        if node in shape.focus_nodes(data):
            found.append(shape.node)
    return sorted(found, key=lambda value: value.n3())


@pytest.mark.parametrize("prepared", [False, True])
@pytest.mark.parametrize("dataset", [False, True])
def test_targeting_matches_reference_for_all_core_targets(prepared, dataset):
    shapes = graph("""ex:Explicit sh:targetNode ex:a, ex:absent, "literal".
        ex:Class sh:targetClass ex:Parent.
        ex:Subjects sh:targetSubjectsOf ex:p.
        ex:Objects sh:targetObjectsOf ex:q.
        ex:Implicit a sh:NodeShape, rdfs:Class.
        ex:Disabled a sh:NodeShape; sh:deactivated true; sh:targetNode ex:a.
        ex:Property a sh:PropertyShape; sh:path ex:p; sh:targetNode ex:a.
        ex:Nested a sh:NodeShape; sh:node [sh:class ex:Parent].""")
    data = graph("""ex:a a ex:Child, ex:Implicit; ex:p 1.
        ex:b ex:q ex:a. ex:Child rdfs:subClassOf ex:Parent.
        ex:Parent rdfs:subClassOf ex:Child.""")
    blank = BNode("target-blank")
    data.add((blank, RDF.type, EX.Parent))
    if dataset:
        source = Dataset(default_union=True)
        source.graph(EX.named).__iadd__(data)
        data = source
    program = turbo.compile_shapes(shapes, advanced=True)
    source = turbo.prepare_target_data(data) if prepared else data
    for node in (EX.a, EX.b, EX.absent, Literal("literal"), blank, EX.none):
        expected = reference_targeting(shapes, data, node)
        assert program.targeting(source, node) == expected
        assert program.targeting(source, node) == expected
    assert EX.Property not in program.targeting(source, EX.a)
    assert EX.Disabled not in program.targeting(source, EX.a)
    assert EX.Nested not in program.targeting(source, EX.a)


def test_targeting_keeps_sparql_limit_semantics_and_skip_sets_independent():
    shapes = graph("""ex:Limited a sh:NodeShape; sh:target [a sh:SPARQLTarget;
        sh:select "SELECT ?this WHERE { ?this <https://example.com/p> 3 } ORDER BY ?this LIMIT 1"].
        ex:Explicit sh:targetNode ex:a, ex:b.""")
    data = graph("ex:a ex:p 3. ex:b ex:p 3.")
    program = turbo.compile_shapes(shapes, advanced=True)
    snapshot = turbo.prepare_target_data(data)
    for node in (EX.a, EX.b):
        for skip in ((), (EX.Explicit,), (EX.Limited,), (EX.absent,)):
            expected = reference_targeting(shapes, data, node, skip)
            assert program.targeting(snapshot, node, skip=skip) == expected
    result = program.targeting(snapshot, EX.a)
    result.clear()
    assert program.targeting(snapshot, EX.a) == [EX.Explicit, EX.Limited]
    assert program.targeting(snapshot, EX.a, skip=iter([EX.Explicit])) == [EX.Limited]


def test_targeting_skip_and_inactive_shapes_prevent_target_evaluation():
    shapes = graph("""ex:Good sh:targetNode ex:a.
        ex:Bad a sh:NodeShape; sh:target [a sh:SPARQLTarget;
          sh:select "SELECT (?missing AS ?this) WHERE {}"].
        ex:Disabled a sh:NodeShape; sh:deactivated true; sh:target [a sh:SPARQLTarget;
          sh:select "SELECT (?missing AS ?this) WHERE {}"].
        ex:Property a sh:PropertyShape; sh:path ex:p; sh:target [a sh:SPARQLTarget;
          sh:select "SELECT (?missing AS ?this) WHERE {}"].""")
    program = turbo.compile_shapes(shapes, advanced=True)
    snapshot = turbo.prepare_target_data(graph(""))
    assert program.targeting(snapshot, EX.a, skip={EX.Bad}) == [EX.Good]
    for _ in range(2):
        with pytest.raises(ValueError, match="unbound"):
            program.targeting(snapshot, EX.a)
    assert program.targeting(snapshot, EX.a, skip={EX.Bad}) == [EX.Good]


def test_targeting_preserves_named_graphs_blank_shapes_and_literal_identity():
    from rdflib.namespace import XSD

    shapes = graph("""[] a sh:NodeShape; sh:targetNode "3", "3"^^xsd:string.
        ex:Named a sh:NodeShape; sh:target [a sh:SPARQLTarget;
          sh:select "SELECT ?this WHERE { GRAPH <https://example.com/first> { ?this <https://example.com/p> 3 } }"] .""")
    data = Dataset(default_union=True)
    data.graph(EX.first).add((EX.a, EX.p, Literal(3)))
    data.graph(EX.second).add((EX.b, EX.p, Literal(3)))
    program = turbo.compile_shapes(shapes, advanced=True)
    snapshot = turbo.prepare_target_data(data)
    for node in (EX.a, EX.b, Literal("3"), Literal("3", datatype=XSD.string)):
        assert program.targeting(snapshot, node) == reference_targeting(shapes, data, node)


def test_targeting_snapshot_lifetime_and_program_identity():
    data = graph("ex:a a ex:Person.")
    shapes = graph("ex:S sh:targetClass ex:Person.")
    program = turbo.compile_shapes(shapes)
    snapshot = turbo.prepare_target_data(data)
    assert program.targeting(snapshot, EX.a) == [EX.S]
    data.remove((EX.a, RDF.type, EX.Person))
    data.add((EX.b, RDF.type, EX.Person))
    assert program.targeting(snapshot, EX.a) == [EX.S]
    assert program.targeting(data, EX.a) == []
    assert program.targeting(data, EX.b) == [EX.S]
    assert program.targeting(turbo.prepare_target_data(data), EX.b) == [EX.S]
    other = turbo.compile_shapes(graph("ex:Other sh:targetNode ex:a."))
    assert other.targeting(snapshot, EX.a) == [EX.Other]
    inspector = turbo.ShapesGraph(shapes)
    assert inspector.targeting(snapshot, EX.a) == [EX.S]


@pytest.mark.parametrize("node,skip", [("urn:node", ()), (EX.a, "urn:shape"), (EX.a, [Literal(3)])])
def test_targeting_rejects_invalid_identifiers(node, skip):
    program = turbo.compile_shapes(graph("ex:S sh:targetNode ex:a."))
    with pytest.raises(TypeError):
        program.targeting(graph(""), node, skip=skip)


def test_inline_typing_marker_is_present():
    assert (Path(turbo.__file__).parent / "py.typed").is_file()


def test_targeting_handles_parameterized_sparql_target_types():
    shapes = graph("""ex:T a sh:SPARQLTargetType; rdfs:subClassOf sh:Target;
        sh:parameter [sh:path ex:class];
        sh:select "SELECT ?this WHERE { ?this a $class }".
        ex:S a sh:NodeShape; sh:target [a ex:T; ex:class ex:Person].""")
    data = graph("ex:a a ex:Person. ex:b a ex:Other.")
    program = turbo.compile_shapes(shapes, advanced=True)
    snapshot = turbo.prepare_target_data(data)
    for node in (EX.a, EX.b):
        assert program.targeting(snapshot, node) == reference_targeting(shapes, data, node)
