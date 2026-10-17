"""Node-expression filters use the same shape evaluator in constraints and rules."""

import pyshacl_turbo as turbo
import pytest
from rdflib import Literal
from rdflib.namespace import SH
from test_compatibility import EX, graph


@pytest.mark.parametrize("allowed,conforms", [("true", True), ("false", False)])
def test_expression_filters_apply_child_shapes_and_keep_expression_messages(allowed, conforms):
    shapes = graph(f"""ex:S sh:targetNode ex:s; sh:message "parent"; sh:expression [
        sh:filterShape ex:Allowed; sh:nodes [sh:union (true false)];
        sh:message "expression-specific"].
        ex:Allowed sh:in ({allowed}).""")
    observed, report, _ = turbo.validate(graph(""), shacl_graph=shapes, advanced=True)
    assert observed is conforms
    if not conforms:
        assert Literal("expression-specific") in set(report.objects(None, SH.resultMessage))
        assert Literal("parent") not in set(report.objects(None, SH.resultMessage))


def test_triple_rule_filters_object_candidates_without_changing_source_data():
    shapes = graph("""ex:S sh:targetNode ex:s; sh:rule [a sh:TripleRule;
        sh:subject sh:this; sh:predicate ex:derived;
        sh:object [sh:filterShape ex:Allowed; sh:nodes [sh:path ex:p]]].
        ex:Allowed sh:in (ex:a).""")
    source = graph("ex:s ex:p ex:a, ex:b.")
    result = turbo.shacl_rules(source, shacl_graph=shapes, advanced=True)
    assert set(result.objects(EX.s, EX.derived)) == {EX.a}
    assert not list(source.objects(EX.s, EX.derived))


@pytest.mark.parametrize("abort,count", [(False, 2), (True, 1)])
def test_abort_on_first_stops_before_the_next_independent_shape(abort, count):
    shapes = graph("""ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1.
        ex:T sh:targetNode ex:s; sh:path ex:q; sh:minCount 1.""")
    conforms, report, _ = turbo.validate(graph(""), shacl_graph=shapes, abort_on_first=abort)
    assert not conforms
    assert len(set(report.subjects(SH.resultSeverity, SH.Violation))) == count


@pytest.mark.parametrize("minimum", [0, 1])
def test_qualified_empty_property_values_obey_the_minimum(minimum):
    shapes = graph(f"""ex:S sh:targetNode ex:s; sh:path ex:p;
        sh:qualifiedValueShape [sh:class ex:Allowed]; sh:qualifiedMinCount {minimum};
        sh:qualifiedMaxCount 1.""")
    conforms, report, _ = turbo.validate(graph(""), shacl_graph=shapes)
    assert conforms is (minimum == 0)
    assert len(list(report.objects(None, SH.sourceConstraintComponent))) == minimum


def test_sparql_constraint_messages_substitute_blank_node_values():
    shapes = graph("""ex:S sh:targetNode ex:s; sh:sparql [
        sh:message "Unexpected {?value}";
        sh:select "SELECT $this ?value WHERE {$this <https://example.com/p> ?value}"].""")
    conforms, report, _ = turbo.validate(graph("ex:s ex:p _:value."), shacl_graph=shapes)
    assert not conforms
    messages = list(report.objects(None, SH.resultMessage))
    assert len(messages) == 1
    assert str(messages[0]).startswith("Unexpected ")
    assert "?value" not in str(messages[0])
