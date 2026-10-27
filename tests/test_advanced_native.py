import pyshacl as original
import pyshacl_turbo as turbo
import pytest
from rdflib import Literal
from rdflib.compare import isomorphic
from rdflib.namespace import SH
from test_compatibility import EX, graph

FUNCTION = """ex:join a sh:SPARQLFunction;
 sh:parameter [sh:path ex:left; sh:order 0];
 sh:parameter [sh:path ex:right; sh:order 1];
 sh:select "SELECT (CONCAT($left, $right) AS ?result) WHERE {}".
"""


def test_triple_rule_function_cartesian_arguments_and_named_graphs():
    import pyoxigraph as ox

    data = ox.Store()
    data.load(
        input=graph('ex:s ex:p "a", "b"; ex:q "1", "2".').serialize(format="nt"),
        format=ox.RdfFormat.N_TRIPLES,
        to_graph=ox.NamedNode(str(EX.g)),
    )
    shapes = graph(
        FUNCTION
        + """ex:S sh:targetNode ex:s; sh:rule [a sh:TripleRule;
      sh:subject sh:this; sh:predicate ex:result;
      sh:object [ex:join ([sh:path ex:p] [sh:path ex:q])]]."""
    )
    result = turbo.shacl_rules(data, shacl_graph=shapes, inplace=True)
    assert set(result.objects(EX.s, EX.result)) == {Literal(s) for s in ("a1", "a2", "b1", "b2")}
    assert len(list(data.quads_for_pattern(None, None, None, ox.NamedNode(str(EX.g))))) == 4


def test_shacl_function_is_invoked_inside_sparql_constraint():
    shapes = graph(
        FUNCTION
        + """ex:S sh:targetNode ex:s; sh:sparql [
      sh:message "joined";
      sh:select 'SELECT $this WHERE { FILTER(ex:join("a", "b") = "ab") }']."""
    )
    conforms, report, _ = turbo.validate(graph(""), shacl_graph=shapes, advanced=True)
    assert not conforms
    assert list(report.objects(None, SH.resultMessage)) == [Literal("joined")]


def test_expression_constraint_requires_one_boolean_true():
    shapes = graph("ex:S sh:targetNode true, false, 1; sh:expression sh:this.")
    conforms, report, _ = turbo.validate(graph(""), shacl_graph=shapes, advanced=True)
    assert not conforms
    assert set(report.objects(None, SH.focusNode)) == {Literal(False), Literal(1)}
    assert set(report.objects(None, SH.sourceConstraint)) == {SH.this}


def test_nested_node_expression_function_and_ask():
    shapes = graph(
        FUNCTION
        + """ex:isAb a sh:SPARQLFunction;
      sh:parameter [sh:path ex:value]; sh:ask 'ASK { FILTER($value = "ab") }'.
      ex:S sh:targetNode ex:s, ex:t;
      sh:expression [ex:isAb ([ex:join ([sh:path ex:p] [sh:path ex:q])])]."""
    )
    conforms, report, _ = turbo.validate(
        graph('ex:s ex:p "a"; ex:q "b". ex:t ex:p "c"; ex:q "b".'),
        shacl_graph=shapes,
        advanced=True,
    )
    assert not conforms
    assert list(report.objects(None, SH.focusNode)) == [EX.t]


def test_custom_sparql_target_type_binds_parameters():
    source = """ex:T a sh:SPARQLTargetType;
      <http://www.w3.org/2000/01/rdf-schema#subClassOf> sh:Target;
      sh:parameter [sh:path ex:class];
      sh:select "SELECT ?this WHERE { ?this a $class }".
      ex:S a sh:NodeShape; sh:target [a ex:T; ex:class ex:C]; sh:class ex:D."""
    conforms, report, text = turbo.validate(
        graph("ex:s a ex:C. ex:t a ex:E."), shacl_graph=graph(source), advanced=True
    )
    expected = original.validate(
        graph("ex:s a ex:C. ex:t a ex:E."), shacl_graph=graph(source), advanced=True
    )
    assert not conforms
    assert list(report.objects(None, SH.focusNode)) == [EX.s]
    assert conforms == expected[0]
    assert isomorphic(report, expected[1])
    assert text == expected[2]


def test_triple_rule_failure_does_not_commit_prior_additions():
    data = graph("ex:s ex:p 1.")
    shapes = graph("""ex:S sh:targetNode ex:s;
      sh:rule [a sh:TripleRule; sh:subject sh:this; sh:predicate ex:q; sh:object 2; sh:order 0],
      [a sh:TripleRule; sh:subject 1; sh:predicate ex:q; sh:object 3; sh:order 1].""")
    before = set(data)
    with pytest.raises((ValueError, RuntimeError)):
        turbo.validate(data, shacl_graph=shapes, advanced=True, inplace=True)
    assert set(data) == before


def test_sparql_function_error_cannot_become_a_conforming_report():
    shapes = graph(
        FUNCTION
        + """ex:S sh:targetNode ex:s; sh:sparql [
      sh:select 'SELECT $this WHERE { FILTER(ex:join("only one") = "ab") }']."""
    )
    with pytest.raises(RuntimeError, match="argument count"):
        turbo.validate(graph(""), shacl_graph=shapes, advanced=True)
