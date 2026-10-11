"""DASH adapters validate expected-result contracts around real native queries."""

import json

import pyshacl_turbo as turbo
import pytest
from pyshacl_turbo import conformance as dash
from rdflib import BNode, Graph, Literal
from rdflib.namespace import OWL, RDF, RDFS, SH
from test_compatibility import EX, graph


def query_case(query="SELECT (1 AS ?value) WHERE {}", expected_value="1"):
    source = graph("")
    source.add((EX.case, RDF.type, dash.DASH.QueryTestCase))
    source.add((EX.case, SH.select, Literal(query)))
    expected = {
        "head": {"vars": ["value"]},
        "results": {
            "bindings": [
                {
                    "value": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": expected_value,
                    }
                }
            ]
        },
    }
    source.add((EX.case, dash.DASH.expectedResult, Literal(json.dumps(expected))))
    return source


@pytest.mark.parametrize("value, matches", [("1", True), ("2", False)])
def test_query_expected_results_use_native_select(value, matches):
    source = query_case(expected_value=value)
    actual, reason = turbo.evaluate_query_testcase(source, EX.case)
    assert actual is matches
    assert (reason is None) is matches
    assert turbo.validate(source, check_dash_result=True)[0] is matches


@pytest.mark.parametrize("field", [SH.select, dash.DASH.expectedResult])
def test_query_case_requires_query_and_expected_results(field):
    source = query_case()
    source.remove((EX.case, field, None))
    with pytest.raises(RuntimeError, match="requires sh:select"):
        turbo.extract_query_and_expected_result(EX.case, source)


def test_query_expected_result_must_be_select():
    source = query_case()
    source.set((EX.case, dash.DASH.expectedResult, Literal('{"head": {}, "boolean": true}')))
    with pytest.raises(RuntimeError, match="expected result must be SELECT"):
        turbo.extract_query_and_expected_result(EX.case, source)


def test_query_actual_result_must_be_select():
    with pytest.raises(RuntimeError, match="query must return SELECT"):
        turbo.evaluate_query_testcase(query_case("ASK {}"), EX.case)


def test_bad_dash_query_counts_as_a_mismatch():
    source = query_case("SELECT malformed")
    assert not turbo.validate(source, check_dash_result=True)[0]


def test_prefix_declarations_follow_import_cycles_and_graph_ontology():
    source = Graph(identifier=EX.document)
    source.add((EX.case, SH.prefixes, EX.first))
    source.add((EX.first, OWL.imports, EX.second))
    source.add((EX.second, OWL.imports, EX.first))
    source.add((EX.ontology, RDF.type, OWL.Ontology))
    for owner, prefix in [
        (EX.first, "first"),
        (EX.second, "second"),
        (EX.ontology, "ont"),
        (EX.document, "doc"),
    ]:
        declaration = BNode()
        source.add((owner, SH.declare, declaration))
        source.add((declaration, SH.prefix, Literal(prefix)))
        source.add((declaration, SH.namespace, Literal(str(EX))))
    prefixes = dash.query_prefixes(source, EX.case)
    for prefix in ("first", "second", "ont", "doc"):
        assert prefixes.count(f"PREFIX {prefix}: <{EX}>") == 1


@pytest.mark.parametrize("missing", [SH.prefix, SH.namespace])
def test_incomplete_prefix_declarations_are_errors(missing):
    source = graph(
        'ex:case sh:prefixes ex:prefixes. ex:prefixes sh:declare [sh:prefix "ex"; sh:namespace "https://example.com/"].'
    )
    source.remove((None, missing, None))
    with pytest.raises(ValueError, match="Incomplete sh:declare"):
        dash.query_prefixes(source, EX.case)


def report():
    source = graph("")
    source.add((EX.report, RDF.type, SH.ValidationReport))
    source.add((EX.report, SH.conforms, Literal(False)))
    source.add((EX.report, SH.result, BNode("result")))
    source.add((BNode("result"), SH.focusNode, EX.s))
    return source


@pytest.mark.parametrize("missing", ["actual-root", "actual-conforms", "expected-conforms"])
def test_report_comparison_rejects_missing_report_contract(missing):
    actual, expected = report(), report()
    if missing == "actual-root":
        actual.remove((EX.report, RDF.type, SH.ValidationReport))
    elif missing == "actual-conforms":
        actual.remove((EX.report, SH.conforms, None))
    else:
        expected.remove((EX.report, SH.conforms, None))
    with pytest.raises(RuntimeError, match="must declare sh:conforms"):
        dash.compare_reports(actual, expected, EX.report)


@pytest.mark.parametrize("messages, details", [(False, False), (True, True)])
def test_report_comparison_preserves_requested_details_and_handles_cycles(messages, details):
    actual, expected = report(), report()
    actual.add((EX.report, RDF.type, RDFS.Resource))
    for source in (actual, expected):
        if source is actual or messages:
            source.add((BNode("result"), SH.resultMessage, Literal("message")))
        if source is actual or details:
            source.add((BNode("result"), SH.detail, BNode("detail")))
            source.add((BNode("detail"), SH.detail, BNode("result")))
    assert dash.compare_reports(actual, expected, EX.report)
    expected.add((BNode("result"), SH.value, EX.wrong))
    assert not dash.compare_reports(actual, expected, EX.report)


@pytest.mark.parametrize(
    "missing",
    [
        "graph-result",
        "inference-result",
        "reified-object",
        "function-expression",
        "function-result",
        "all-cases",
    ],
)
def test_dash_cases_require_complete_expected_contracts(missing):
    if missing == "graph-result":
        source = graph("")
        source.add((EX.case, RDF.type, dash.DASH.GraphValidationTestCase))
    elif missing in {"inference-result", "reified-object"}:
        source = graph("")
        source.add((EX.case, RDF.type, dash.DASH.InferencingTestCase))
        if missing == "reified-object":
            source.add((EX.case, dash.DASH.expectedResult, EX.triple))
            source.add((EX.triple, RDF.subject, EX.s))
            source.add((EX.triple, RDF.predicate, EX.p))
    elif missing.startswith("function"):
        source = graph("")
        source.add((EX.case, RDF.type, dash.DASH.FunctionTestCase))
        source.add((EX.case, dash.DASH.expression, Literal("1 + 1")))
        source.add((EX.case, dash.DASH.expectedResult, Literal(2)))
        source.remove(
            (
                EX.case,
                dash.DASH.expression
                if missing == "function-expression"
                else dash.DASH.expectedResult,
                None,
            )
        )
    else:
        source = graph("")
    with pytest.raises(RuntimeError):
        dash.check_dash_result(report(), source, graph(""))


def test_multiple_inference_cases_share_the_expanded_graph():
    source = graph("ex:s ex:p ex:t.")
    for case in (EX.one, EX.two):
        triple = BNode()
        source.add((case, RDF.type, dash.DASH.InferencingTestCase))
        source.add((case, dash.DASH.expectedResult, triple))
        for predicate, value in [(RDF.subject, EX.s), (RDF.predicate, EX.p), (RDF.object, EX.t)]:
            source.add((triple, predicate, value))
    assert turbo.validate(source, check_dash_result=True)[0]


@pytest.mark.parametrize("actual", [EX.resource, Literal("different", datatype=EX.opaque)])
def test_inference_expected_literals_reject_nonliterals_and_incomparable_values(actual):
    assert not dash._literal_matches(Literal("expected", datatype=EX.opaque), actual)


@pytest.mark.parametrize("expected, matches", [(2, True), (3, False)])
def test_function_expected_results_use_native_sparql(expected, matches):
    source = graph("")
    source.add((EX.case, RDF.type, dash.DASH.FunctionTestCase))
    source.add((EX.case, dash.DASH.expression, Literal("1 + 1")))
    source.add((EX.case, dash.DASH.expectedResult, Literal(expected)))
    assert turbo.validate(source, check_dash_result=True)[0] is matches
