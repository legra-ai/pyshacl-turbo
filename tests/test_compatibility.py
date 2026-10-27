"""Behavioral contract: independently compare reports and derived graphs to pySHACL."""

from pathlib import Path

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import RDF, BNode, Dataset, Graph, Literal, Namespace
from rdflib.compare import isomorphic

EX = Namespace("https://example.com/")
SH = Namespace("http://www.w3.org/ns/shacl#")
PREFIXES = """
@prefix ex: <https://example.com/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""
FIXTURES = Path(__file__).parent / "fixtures"


def graph(body):
    return Graph().parse(data=PREFIXES + body, format="turtle")


def reference_rules(data, shapes, **options):
    # 0.40.1 returns a DataGraph wrapper whose iteration yields quads even for
    # Graph inputs. Assert single-graph semantics before reading its triples.
    result = pyshacl.shacl_rules(data, shacl_graph=shapes, advanced=True, **options)
    assert not result.is_multigraph()
    output = Graph()
    for triple in result.triples((None, None, None)):
        output.add(triple)
    return output


def compare(data, shapes, **options):
    expected = pyshacl.validate(data, shacl_graph=shapes, advanced=True, **options)
    actual = turbo.validate(data, shacl_graph=shapes, advanced=True, **options)
    assert actual[0] == expected[0]
    assert isomorphic(actual[1], expected[1]), (
        actual[1].serialize(format="turtle"),
        expected[1].serialize(format="turtle"),
    )
    assert isinstance(actual[2], str)
    return actual


def test_complete_pipeline_matches_report_and_expansion():
    data = Graph().parse(FIXTURES / "pipeline-data.ttl")
    shapes = Graph().parse(FIXTURES / "pipeline-shapes.ttl")
    before = set(data)
    conforms, report, _ = compare(data, shapes)
    assert not conforms
    assert set(report.objects(None, SH.focusNode)) == {EX.bob}
    expected = reference_rules(data, shapes)
    actual = turbo.shacl_rules(data, shacl_graph=shapes, advanced=True)
    assert isomorphic(actual, expected)
    assert (EX.alice, EX.eligible, Literal(True)) in actual
    assert (EX.bob, EX.eligible, Literal(True)) in actual
    assert (EX.carol, EX.eligible, Literal(True)) not in actual
    assert set(data) == before


@pytest.mark.parametrize(
    "target,data",
    [
        ("sh:targetNode ex:alice", ""),
        (
            "sh:targetClass ex:Person",
            "ex:alice a ex:Employee . ex:Employee rdfs:subClassOf ex:Person .",
        ),
        (
            "sh:targetClass ex:Person",
            "ex:alice a ex:Employee . ex:Employee rdfs:subClassOf ex:Manager . ex:Manager rdfs:subClassOf ex:Person . ex:Person rdfs:subClassOf ex:Employee .",
        ),
        ("sh:targetSubjectsOf ex:name", 'ex:alice ex:name "Alice" .'),
        ("sh:targetObjectsOf ex:knows", "ex:bob ex:knows ex:alice ."),
        (
            'sh:target [a sh:SPARQLTarget; sh:select "SELECT ?this WHERE { BIND(<https://example.com/alice> AS ?this) }"]',
            "",
        ),
    ],
)
def test_target_selection(target, data):
    shapes = graph(
        f'ex:S a sh:NodeShape; {target}; sh:property ex:P. ex:P sh:path ex:email; sh:minCount 1; sh:message "missing".'
    )
    _, report, _ = compare(graph(data), shapes)
    assert set(report.objects(None, SH.focusNode)) == {EX.alice}


@pytest.mark.parametrize(
    "constraint,values",
    [
        ("sh:minCount 1", ""),
        ("sh:maxCount 1", 'ex:alice ex:p "a", "b".'),
        ("sh:hasValue ex:required", "ex:alice ex:p ex:other."),
        ("sh:minCount 1", 'ex:alice ex:p "a".'),
        ("sh:maxCount 1", 'ex:alice ex:p "a".'),
        ("sh:hasValue ex:required", "ex:alice ex:p ex:required."),
    ],
)
def test_constraint_reports(constraint, values):
    compare(
        graph(values),
        graph(
            f'ex:S a sh:NodeShape; sh:targetNode ex:alice; sh:property ex:P. ex:P sh:path ex:p; {constraint}; sh:message "bad value".'
        ),
    )


def test_blank_node_source_shape_and_focus_identity():
    data = graph('_:alice ex:name "Alice".')
    shapes = graph(
        'ex:S a sh:NodeShape; sh:targetSubjectsOf ex:name; sh:property [sh:path ex:email; sh:minCount 1; sh:message "missing"].'
    )
    _, report, _ = compare(data, shapes)
    assert set(report.objects(None, SH.focusNode)) == set(data.subjects(EX.name))
    assert set(report.objects(None, SH.sourceShape)) == set(shapes.objects(EX.S, SH.property))


def test_multiple_messages_and_severity():
    compare(
        graph(""),
        graph(
            'ex:S a sh:NodeShape; sh:targetNode ex:alice; sh:property ex:P. ex:P sh:path ex:p; sh:minCount 1; sh:severity sh:Warning; sh:message "missing"@en, "ontbreekt"@nl.'
        ),
    )


def test_deactivated_shape_and_rule():
    data = graph("ex:alice a ex:Person.")
    shapes = graph("""
        ex:S a sh:NodeShape; sh:targetClass ex:Person; sh:deactivated true;
          sh:property [sh:path ex:p; sh:minCount 1; sh:message "missing"].
        ex:T a sh:NodeShape; sh:targetClass ex:Person; sh:rule ex:R.
        ex:R a sh:SPARQLRule; sh:deactivated true;
          sh:construct "CONSTRUCT { $this <https://example.com/p> true } WHERE {}".
    """)
    compare(data, shapes)
    assert isomorphic(turbo.shacl_rules(data, shacl_graph=shapes, advanced=True), data)


def test_rule_order_conditions_and_deferred_insertions():
    shapes = graph("""
        ex:S a sh:NodeShape; sh:targetNode ex:alice; sh:rule ex:Second, ex:First.
        ex:First a sh:SPARQLRule; sh:order 0.5;
          sh:construct "CONSTRUCT { $this <https://example.com/ready> true } WHERE {}".
        ex:Second a sh:SPARQLRule; sh:order 1.5; sh:condition ex:C;
          sh:construct "CONSTRUCT { $this <https://example.com/done> true } WHERE {}".
        ex:C sh:property [sh:path ex:ready; sh:hasValue true].
    """)
    actual = turbo.shacl_rules(graph(""), shacl_graph=shapes, advanced=True)
    expected = reference_rules(graph(""), shapes)
    assert isomorphic(actual, expected)
    assert (EX.alice, EX.done, Literal(True)) in actual


@pytest.mark.parametrize("iterate", [False, True])
def test_rule_iteration(iterate):
    data = graph("ex:alice ex:reachable ex:a. ex:a ex:next ex:b. ex:b ex:next ex:c.")
    shapes = graph('''
        ex:S a sh:NodeShape; sh:targetNode ex:alice; sh:rule ex:R.
        ex:R a sh:SPARQLRule; sh:construct """
          PREFIX ex: <https://example.com/>
          CONSTRUCT { $this ex:reachable ?next }
          WHERE { $this ex:reachable ?current. ?current ex:next ?next }
        """.
    ''')
    actual = turbo.shacl_rules(data, shacl_graph=shapes, advanced=True, iterate_rules=iterate)
    expected = reference_rules(data, shapes, iterate_rules=iterate)
    assert isomorphic(actual, expected)
    assert ((EX.alice, EX.reachable, EX.c) in actual) is iterate


def test_nonterminating_rule_is_a_hard_error():
    shapes = graph("""
      ex:S a sh:NodeShape; sh:targetNode ex:alice; sh:rule ex:R.
      ex:R a sh:SPARQLRule;
        sh:construct "CONSTRUCT { $this <https://example.com/p> [] } WHERE {}".
    """)
    with pytest.raises(RuntimeError, match="iteration"):
        turbo.shacl_rules(
            graph(""), shacl_graph=shapes, advanced=True, iterate_rules=True, max_rule_iterations=3
        )


def test_compiled_shapes_reuse_without_leaking_data():
    shapes = graph(
        'ex:S a sh:NodeShape; sh:targetNode ex:alice; sh:property ex:P. ex:P sh:path ex:p; sh:minCount 1; sh:message "missing".'
    )
    compiled = turbo.compile_shapes(shapes)
    assert not compiled.validate(graph(""))[0]
    assert compiled.validate(graph('ex:alice ex:p "present".'))[0]
    assert not compiled.validate(graph(""))[0]


def test_inplace_preserves_existing_blank_nodes():
    data = graph("_:alice a ex:Person.")
    original = next(data.subjects(RDF.type, EX.Person))
    assert isinstance(original, BNode)
    shapes = graph("""
      ex:S a sh:NodeShape; sh:targetClass ex:Person; sh:rule ex:R.
      ex:R a sh:SPARQLRule; sh:construct "CONSTRUCT { $this <https://example.com/p> true } WHERE {}".
    """)
    turbo.validate(data, shacl_graph=shapes, advanced=True, inplace=True)
    assert (original, EX.p, Literal(True)) in data
    assert set(data.subjects(RDF.type, EX.Person)) == {original}


@pytest.mark.parametrize("feature", ["sh:js ex:JS"])
def test_unsupported_features_never_silently_pass(feature):
    with pytest.raises(NotImplementedError, match="Unsupported"):
        turbo.validate(
            graph(""), shacl_graph=graph(f"ex:S a sh:NodeShape; sh:targetNode ex:alice; {feature}.")
        )


def test_complex_property_paths_validate():
    compare(
        graph(""),
        graph(
            'ex:S a sh:NodeShape; sh:targetNode ex:alice; sh:property [sh:path (ex:p ex:q); sh:minCount 1; sh:message "missing"].'
        ),
    )


@pytest.mark.parametrize("options", [{"js": True}, {"typo": True}])
def test_unsupported_options_rejected(options):
    with pytest.raises((NotImplementedError, TypeError)):
        turbo.validate(graph(""), shacl_graph=graph(""), **options)


def test_dataset_preserves_named_graphs_for_sparql():
    data = Dataset()
    data.graph(EX.named).add((EX.s, EX.p, Literal(1)))
    shapes = graph("""ex:S sh:targetNode ex:s; sh:sparql [sh:message "named";
      sh:select "SELECT $this WHERE { GRAPH <https://example.com/named> { $this ?p ?o } }"].""")
    conforms, report, _ = turbo.validate(data, shacl_graph=shapes)
    assert not conforms
    assert list(report.objects(None, SH.focusNode)) == [EX.s]


def test_malformed_query_rejected_at_compile_time():
    with pytest.raises(ValueError, match="SPARQL"):
        turbo.compile_shapes(
            graph('ex:S a sh:NodeShape; sh:target [a sh:SPARQLTarget; sh:select "SELECT ???"].'),
            advanced=True,
        )


def test_file_and_turtle_inputs():
    data = FIXTURES / "pipeline-data.ttl"
    shapes = FIXTURES / "pipeline-shapes.ttl"
    actual = turbo.validate(data, shacl_graph=shapes, advanced=True)
    from_text = turbo.validate(
        data.read_text(),
        shacl_graph=shapes.read_text(),
        data_graph_format="turtle",
        shacl_graph_format="turtle",
        advanced=True,
    )
    assert isomorphic(actual[1], from_text[1])
