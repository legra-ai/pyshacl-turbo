"""Behavior preserved across the shared structural-model compiler boundary."""

import pytest
from rdflib.namespace import SH
from test_compatibility import EX, compare, graph


def test_display_defaults_do_not_activate_cardinality_validation():
    shapes = graph("""ex:P a sh:PropertyShape; sh:targetNode ex:s;
        sh:path ex:p; sh:defaultValue 1, 2.""")
    assert compare(graph(""), shapes)[0]


@pytest.mark.parametrize("target_type", ["ex:People", "_:people"])
def test_custom_target_type_retains_rdf_identity(target_type):
    shapes = graph(f"""{target_type} a sh:SPARQLTargetType; rdfs:subClassOf sh:Target;
        sh:parameter [sh:path ex:class];
        sh:select "SELECT ?this WHERE {{ ?this a $class }}".
        ex:S a sh:NodeShape; sh:target [a {target_type}; ex:class ex:Person];
        sh:class ex:Missing.""")
    conforms, report, _ = compare(graph("ex:s a ex:Person. ex:t a ex:Other."), shapes)
    assert not conforms
    assert set(report.objects(None, SH.focusNode)) == {EX.s}
