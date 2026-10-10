import pyshacl_turbo as turbo
import pytest
from rdflib import BNode, Graph, Literal
from rdflib.compare import isomorphic
from test_compatibility import EX, SH, compare, graph, reference_rules


def test_condition_lists_cannot_silently_become_unconstrained_shapes():
    shapes = graph("""
        ex:S a sh:NodeShape; sh:targetNode ex:alice; sh:rule ex:R.
        ex:R a sh:SPARQLRule; sh:condition (ex:C);
          sh:construct "CONSTRUCT { $this <https://example.com/p> true } WHERE {}".
        ex:C sh:property [sh:path ex:missing; sh:hasValue true].
    """)
    for data in [graph(""), graph("ex:alice ex:missing true.")]:
        assert isomorphic(
            turbo.shacl_rules(data, shacl_graph=shapes), reference_rules(data, shapes)
        )


def test_constant_construct_without_this_variable():
    shapes = graph("""
        ex:S a sh:NodeShape; sh:targetNode ex:alice; sh:rule ex:R.
        ex:R a sh:SPARQLRule;
          sh:construct "CONSTRUCT { <https://example.com/constant> <https://example.com/p> true } WHERE {}".
    """)
    assert isomorphic(
        turbo.shacl_rules(graph(""), shacl_graph=shapes), reference_rules(graph(""), shapes)
    )


def test_rule_additions_not_visible_between_focus_nodes():
    shapes = graph('''
        ex:S a sh:NodeShape; sh:targetNode ex:a, ex:b; sh:rule ex:R.
        ex:R a sh:SPARQLRule; sh:construct """
          PREFIX ex: <https://example.com/>
          CONSTRUCT { $this ex:eligible true }
          WHERE { FILTER NOT EXISTS { ?any ex:eligible true } }
        """.
    ''')
    actual = turbo.shacl_rules(graph(""), shacl_graph=shapes)
    assert isomorphic(actual, reference_rules(graph(""), shapes))
    assert set(actual.subjects(EX.eligible, Literal(True))) == {EX.a, EX.b}


def test_implicit_class_target():
    compare(
        graph("ex:alice a ex:Person."),
        graph("""
        ex:Person a sh:NodeShape, rdfs:Class; sh:property ex:P.
        ex:P sh:path ex:p; sh:minCount 1; sh:message "missing".
    """),
    )


def test_failed_inplace_run_does_not_commit_partial_rule_results():
    data = graph("ex:alice a ex:Person.")
    before = set(data)
    shapes = graph("""
        ex:S a sh:NodeShape; sh:targetNode ex:alice; sh:rule ex:R.
        ex:R a sh:SPARQLRule;
          sh:construct "CONSTRUCT { $this <https://example.com/p> [] } WHERE {}".
    """)
    with pytest.raises(RuntimeError, match="iteration"):
        turbo.validate(
            data,
            shacl_graph=shapes,
            advanced=True,
            inplace=True,
            iterate_rules=True,
            max_rule_iterations=2,
        )
    assert set(data) == before


def test_unknown_target_type_rejected():
    with pytest.raises(NotImplementedError, match="target type"):
        turbo.compile_shapes(graph("ex:S a sh:NodeShape; sh:target [a ex:Unknown]."), advanced=True)


def test_missing_target_projection_fails_during_compilation():
    with pytest.raises(ValueError, match="this"):
        turbo.compile_shapes(
            graph(
                'ex:S a sh:NodeShape; sh:target [a sh:SPARQLTarget; sh:select "SELECT ?wrong WHERE {}"].'
            ),
            advanced=True,
        )


@pytest.mark.parametrize(
    "definition",
    [
        "sh:minCount -1",
        "sh:minCount 1, 2",
        'sh:minCount "1"',
        'sh:deactivated "true"',
        'sh:severity "error"',
    ],
)
def test_malformed_shapes_are_errors(definition):
    with pytest.raises(ValueError):
        turbo.compile_shapes(graph(f"ex:S a sh:PropertyShape; sh:path ex:p; {definition}."))


def test_rust_parser_preserves_relative_file_base(tmp_path):
    data = tmp_path / "data.ttl"
    shapes = tmp_path / "shapes.ttl"
    data.write_text("<#alice> <https://example.com/p> true.")
    shapes.write_text(f"""@prefix sh: <{SH}>.
        <#S> a sh:NodeShape; sh:targetNode <{data.as_uri()}#alice>;
          sh:property [sh:path <https://example.com/p>; sh:minCount 1].""")
    assert turbo.validate(data, shacl_graph=shapes)[0]


def test_recursive_property_shapes_without_targets_are_valid():
    program = turbo.compile_shapes(
        graph("ex:S a sh:PropertyShape; sh:path ex:p; sh:property ex:S.")
    )
    assert program.validate(graph(""))[0]


def test_blank_nodes_created_by_rules_share_identity_between_report_and_data():
    data = graph("")
    shapes = graph("""
        ex:S a sh:NodeShape; sh:targetNode ex:alice; sh:rule ex:R.
        ex:R a sh:SPARQLRule;
          sh:construct "CONSTRUCT { $this <https://example.com/child> [a <https://example.com/Child>] } WHERE {}".
        ex:T a sh:NodeShape; sh:targetClass ex:Child; sh:property ex:P.
        ex:P sh:path ex:name; sh:minCount 1; sh:message "missing".
    """)
    _, report, _ = turbo.validate(data, shacl_graph=shapes, advanced=True, inplace=True)
    child = next(data.objects(EX.alice, EX.child))
    assert isinstance(child, BNode)
    assert set(report.objects(None, SH.focusNode)) == {child}


def test_same_explicit_blank_node_can_be_targeted_across_graphs():
    node = BNode("shared")
    data = Graph()
    data.add((node, EX.p, Literal(True)))
    shapes = graph(
        'ex:S a sh:NodeShape; sh:property ex:P. ex:P sh:path ex:p; sh:minCount 1; sh:message "missing".'
    )
    shapes.add((EX.S, SH.targetNode, node))
    assert compare(data, shapes)[0]


def test_rule_and_target_prefix_declarations():
    shapes = graph("""
        ex:Prefixes sh:declare [sh:prefix "ex"; sh:namespace "https://example.com/"^^xsd:anyURI].
        ex:S a sh:NodeShape; sh:target [a sh:SPARQLTarget; sh:prefixes ex:Prefixes;
            sh:select "SELECT ?this WHERE { ?this a ex:C }"];
          sh:rule [a sh:SPARQLRule; sh:prefixes ex:Prefixes;
            sh:construct "CONSTRUCT { $this ex:bound true } WHERE { FILTER(BOUND($this)) }"].
    """)
    data = graph("ex:a a ex:C.")
    assert isomorphic(turbo.shacl_rules(data, shacl_graph=shapes), reference_rules(data, shapes))
