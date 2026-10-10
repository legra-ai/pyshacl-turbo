import pyshacl_turbo as turbo
from rdflib import Graph
from test_compatibility import PREFIXES, graph


def test_report_text_is_stable_when_parser_renames_blank_nodes():
    shapes = (
        PREFIXES
        + """ex:S sh:targetNode ex:s; sh:property
        [sh:path ex:p; sh:minCount 1], [sh:path ex:q; sh:maxCount 1]."""
    )
    data = PREFIXES + 'ex:s ex:q [ex:name "a"], [ex:name "b"].'
    outputs = [
        turbo.validate(
            Graph().parse(data=data, format="turtle"),
            shacl_graph=Graph().parse(data=shapes, format="turtle"),
        )[2]
        for _ in range(3)
    ]
    assert outputs[0] == outputs[1] == outputs[2]
    assert "Constraint Violation in MinCountConstraintComponent" in outputs[0]
    assert "Focus Node: ex:s" in outputs[0]
    assert "_:" not in outputs[0]


def test_node_constraint_message_names_all_referenced_shapes():
    shapes = graph("""ex:S sh:targetNode ex:s; sh:node ex:A, ex:B.
      ex:A sh:class ex:A. ex:B sh:class ex:B.""")
    _, _, text = turbo.validate(graph(""), shacl_graph=shapes)
    assert "Value must conform to every Shape in ('ex:A', 'ex:B')" in text


def test_not_constraint_report_uses_data_prefix_for_focus_node():
    data = graph("ex:s a ex:C.")
    data.bind("kb", "https://kb.example/")
    shapes = graph("ex:S sh:targetNode <https://kb.example/s>; sh:not [sh:nodeKind sh:IRI].")
    _, _, text = turbo.validate(data, shacl_graph=shapes)
    assert "Node kb:s must not conform to shape" in text
