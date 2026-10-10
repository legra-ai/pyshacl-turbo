import pyshacl_turbo as turbo
import pytest
from rdflib import Literal
from suite_harness import cases
from suite_harness import compare as compare_w3c
from test_compatibility import EX, SH, compare, graph


@pytest.mark.parametrize("case", cases("sparql"), ids=lambda c: c.id)
def test_w3c_sparql_constraint(case):
    compare_w3c(case, turbo.validate)


@pytest.mark.parametrize("path", ["ex:p", "(ex:p ex:q)", "[sh:inversePath ex:p]"])
def test_sparql_path_prebinding_and_messages(path):
    compare(
        graph('ex:s ex:p ex:t. ex:t ex:p ex:s; ex:q "bad".'),
        graph(f"""
        ex:S sh:targetNode ex:s; sh:path {path}; sh:sparql ex:C.
        ex:C sh:message "bad {{?value}} on {{$this}}";
          sh:select "SELECT $this ?value WHERE {{ $this $PATH ?value }}".
    """),
    )


def test_path_text_in_literal_and_comment_is_not_substituted():
    compare(
        graph('ex:s ex:p "value".'),
        graph('''
        ex:S sh:targetNode ex:s; sh:path ex:p; sh:sparql ex:C.
        ex:C sh:message "literal"; sh:select """
            SELECT $this ?value WHERE {
                $this $PATH ?value .
                FILTER ("$PATH" = "$PATH") # $PATH must not rewrite this comment
            }
        """.
    '''),
    )


def test_sparql_deactivation():
    assert turbo.validate(
        graph(""),
        shacl_graph=graph("""
        ex:S sh:targetNode ex:s; sh:sparql [sh:deactivated true; sh:select "SELECT $this WHERE {}"].
    """),
    )[0]


def test_sparql_duplicate_rows_do_not_duplicate_results():
    _, report, _ = compare(
        graph("ex:s ex:p 1, 2."),
        graph("""
        ex:S sh:targetNode ex:s; sh:sparql ex:C.
        ex:C sh:message "bad"; sh:select "SELECT $this WHERE { $this <https://example.com/p> ?ignored }".
    """),
    )
    assert len(list(report.objects(None, SH.result))) == 1


def test_sparql_report_path_override():
    compare(
        graph("ex:s ex:p 1."),
        graph("""
        ex:S sh:targetNode ex:s; sh:sparql ex:C.
        ex:C sh:message "bad"; sh:select "SELECT $this ?path ?value WHERE { $this ?path ?value }".
    """),
    )


def test_forbidden_construct_inside_exists_is_detected():
    with pytest.raises(ValueError, match="VALUES"):
        turbo.compile_shapes(
            graph("""ex:S sh:targetNode ex:s; sh:sparql [
            sh:select "SELECT $this WHERE { FILTER EXISTS { VALUES ?v { 1 } } }"].""")
        )


def test_sparql_current_shape_prebinding():
    _, report, _ = turbo.validate(
        graph(""),
        shacl_graph=graph("""
        ex:S sh:targetNode ex:s; sh:sparql [sh:message "current";
          sh:select "SELECT $this WHERE { FILTER($currentShape = <https://example.com/S>) }"].
    """),
    )
    assert list(report.objects(None, SH.resultMessage)) == [Literal("current")]


def test_custom_ask_validator_matches_complete_report():
    compare(
        graph('ex:s ex:p "yes", "no".'),
        graph("""
        ex:Component a sh:ConstraintComponent; sh:parameter [sh:path ex:expected];
            sh:validator [a sh:SPARQLAskValidator; sh:message "expected {?expected}";
                sh:ask "ASK { FILTER($value = $expected) }"].
        ex:S sh:targetNode ex:s; sh:property ex:P.
        ex:P sh:path ex:p; ex:expected "yes".
    """),
    )


def test_custom_select_validator():
    compare(
        graph("ex:s ex:p 1, 2, 3."),
        graph("""
        ex:Component a sh:ConstraintComponent; sh:parameter [sh:path ex:expected];
            sh:propertyValidator [a sh:SPARQLSelectValidator; sh:message "expected {?expected}";
                sh:select "SELECT $this ?value WHERE { $this $PATH ?value FILTER(?value != $expected) }"].
        ex:P sh:targetNode ex:s; sh:path ex:p; ex:expected 2.
    """),
    )


def test_custom_component_does_not_activate_without_required_parameter():
    assert turbo.validate(
        graph(""),
        shacl_graph=graph("""
        ex:Component a sh:ConstraintComponent; sh:parameter [sh:path ex:expected];
          sh:validator [sh:ask "ASK { FILTER(false) }"].
        ex:S sh:targetNode ex:s.
    """),
    )[0]


def test_custom_node_select_validator():
    compare(
        graph("ex:s ex:p 1."),
        graph("""
        ex:Component a sh:ConstraintComponent; sh:parameter [sh:path ex:expected];
          sh:nodeValidator [sh:message "bad";
            sh:select "SELECT $this WHERE { FILTER NOT EXISTS { $this <https://example.com/p> $expected } }"].
        ex:S sh:targetNode ex:s; ex:expected 2.
    """),
    )


def test_custom_parameter_values_create_all_constraint_combinations():
    # pySHACL 0.40.1 bind_params selects an arbitrary single value (upstream
    # TODO). SHACL creates a constraint for every parameter-value combination.
    _, report, _ = turbo.validate(
        graph("ex:s ex:p 1, 2, 3."),
        shacl_graph=graph("""
        ex:Component a sh:ConstraintComponent; sh:parameter [sh:path ex:expected];
          sh:propertyValidator [sh:message "expected {?expected}";
            sh:select "SELECT $this ?value WHERE { $this $PATH ?value FILTER(?value != $expected) }"].
        ex:P sh:targetNode ex:s; sh:path ex:p; ex:expected 1, 2.
    """),
    )
    assert sorted(
        (str(report.value(r, SH.resultMessage)), int(report.value(r, SH.value)))
        for r in report.objects(None, SH.result)
    ) == [("expected 1", 2), ("expected 1", 3), ("expected 2", 1), ("expected 2", 3)]


def test_external_focus_variable_is_legal_in_aggregate_subquery():
    data = graph("ex:s ex:p 1, 2.")
    shapes = graph("""ex:S sh:targetNode ex:s; sh:sparql [sh:message "aggregate";
      sh:select "SELECT $this WHERE { { SELECT $this ?p (COUNT(?v) AS ?n) WHERE { $this ?p ?v } GROUP BY ?p } FILTER (?n = 2) }"].""")
    conforms, report, _ = turbo.validate(data, shacl_graph=shapes)
    assert not conforms
    assert list(report.objects(None, SH.focusNode)) == [EX.s]
