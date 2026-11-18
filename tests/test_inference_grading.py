"""Acceptance-harness regressions, not inference-engine conformance results."""

import pytest
from rdflib import BNode, Graph, Literal, Namespace
from w3c_grading import W3C_SHACL12, CaseType, Outcome
from w3c_inference import InferenceFixture

EX = Namespace("http://example.com/ns#")


@pytest.fixture(scope="module")
def cases():
    return {
        case.path.stem: case for case in W3C_SHACL12.discover() if case.case_type is CaseType.INFER
    }


def test_same_order_expected_triples_are_read_from_the_original_manifest(cases):
    fixture = InferenceFixture.read(cases["same-order"])
    assert set(fixture.expected) == {
        (EX.SomeNode, EX.p, Literal(True)),
        (EX.SomeNode, EX.q, Literal(True)),
    }
    assert fixture.data is fixture.shapes
    assert len(fixture.data) > len(fixture.expected)


def test_external_expected_graph_is_read_without_base_or_manifest_triples(cases):
    fixture = InferenceFixture.read(cases["layers-example"])
    assert len(fixture.expected) == 16
    assert fixture.expected is not fixture.data


def test_comparison_is_exact_and_blank_node_isomorphic(cases):
    fixture = InferenceFixture.read(cases["run-once-shared-shapes"])
    actual = Graph().add((EX.ExampleItem, EX.head, BNode()))
    assert fixture.grade(lambda data, shapes: actual, ValueError).outcome is Outcome.PASS
    actual.add((EX.ExampleItem, EX.head, BNode()))
    assert fixture.grade(lambda data, shapes: actual, ValueError).outcome is Outcome.FAIL


def test_base_graph_is_not_accepted_as_the_inferred_graph(cases):
    fixture = InferenceFixture.read(cases["same-order"])
    assert fixture.grade(lambda data, shapes: data, ValueError).outcome is Outcome.FAIL


@pytest.mark.parametrize("error, outcome", [(ValueError, Outcome.PASS), (TypeError, Outcome.ERROR)])
def test_only_declared_engine_failures_satisfy_a_failure_expectation(cases, error, outcome):
    fixture = InferenceFixture.read(cases["SPARQLRule-syntax-error"])

    def run(data, shapes):
        raise error("failure")

    assert fixture.grade(run, ValueError).outcome is outcome


def test_inputs_are_immutable_even_when_execution_reports_a_failure(cases):
    fixture = InferenceFixture.read(cases["SPARQLRule-syntax-error"])

    def run(data, shapes):
        data.add((EX.corruption, EX.p, EX.o))
        raise ValueError("failure")

    grade = fixture.grade(run, ValueError)
    assert grade.outcome is Outcome.FAIL
    assert grade.detail == "input graph mutated"


def test_a_successful_graph_does_not_satisfy_an_expected_failure(cases):
    fixture = InferenceFixture.read(cases["SPARQLRule-syntax-error"])
    assert fixture.grade(lambda data, shapes: Graph(), ValueError).outcome is Outcome.FAIL


def test_projected_rdf12_inputs_never_reach_the_runner(cases):
    from dataclasses import replace

    case = replace(cases["same-order"], rdf12_syntax=True)
    with pytest.raises(ValueError, match="RDF 1.2"):
        InferenceFixture.read(case)
