"""DASH expected-result adapters. SPARQL execution remains in the Rust engine."""

from io import StringIO

from rdflib import BNode, Graph, Literal, Namespace
from rdflib.compare import isomorphic
from rdflib.namespace import OWL, RDF, RDFS, SH
from rdflib.query import Result

from . import _native
from .rdf import input_graph, union

DASH = Namespace("http://datashapes.org/dash#")


def query_prefixes(graph, node):
    prefixes = dict(graph.namespaces())
    pending, seen = list(graph.objects(node, SH.prefixes)), set()
    if pending:
        pending.extend(graph.subjects(RDF.type, OWL.Ontology))
        pending.append(graph.identifier)
    while pending:
        resource = pending.pop()
        if resource in seen:
            continue
        seen.add(resource)
        pending.extend(graph.objects(resource, OWL.imports))
        for declaration in graph.objects(resource, SH.declare):
            prefix = graph.value(declaration, SH.prefix, any=False)
            namespace = graph.value(declaration, SH.namespace, any=False)
            if prefix is None or namespace is None:
                raise ValueError("Incomplete sh:declare")
            prefixes[str(prefix)] = namespace
    return "".join(f"PREFIX {p}: <{ns}>\n" for p, ns in sorted(prefixes.items()))


def extract_query_and_expected_result(test_case, graph, log=None):
    text = graph.value(test_case, SH.select, any=False)
    expected = graph.value(test_case, DASH.expectedResult, any=False)
    if text is None or expected is None:
        raise RuntimeError("QueryTestCase requires sh:select and dash:expectedResult")
    result = Result.parse(StringIO(str(expected)), format="json")
    if result.type != "SELECT":
        raise RuntimeError("QueryTestCase expected result must be SELECT")
    return query_prefixes(graph, test_case) + str(text), result


def evaluate_query_testcase(query_graph, test_case, log=None):
    query, expected = extract_query_and_expected_result(test_case, query_graph, log)
    snapshot = input_graph(query_graph)
    actual = Result.parse(
        StringIO(_native.query(snapshot.source, snapshot.format, query)), format="json"
    )
    if actual.type != "SELECT":
        raise RuntimeError("QueryTestCase query must return SELECT results")
    matches = set(actual.vars) == set(expected.vars) and [row.asdict() for row in actual] == [
        row.asdict() for row in expected
    ]
    return matches, None if matches else "SPARQL SELECT result differs from dash:expectedResult"


def report_subgraph(graph, root, messages, details):
    result, seen, pending = Graph(), set(), [root]
    while pending:
        node = pending.pop()
        if node in seen:
            continue
        seen.add(node)
        for _, predicate, value in graph.triples((node, None, None)):
            if (
                (predicate == RDF.type and value == RDFS.Resource)
                or (predicate == SH.resultMessage and not messages)
                or (predicate == SH.detail and not details)
            ):
                continue
            result.add((node, predicate, value))
            if isinstance(value, BNode):
                pending.append(value)
    return result


def compare_reports(actual, expected, expected_root):
    actual_root = actual.value(None, RDF.type, SH.ValidationReport, any=False)
    if (
        actual_root is None
        or actual.value(actual_root, SH.conforms) is None
        or expected.value(expected_root, SH.conforms) is None
    ):
        raise RuntimeError("Expected and actual reports must declare sh:conforms")
    expected_results = list(expected.objects(expected_root, SH.result))
    messages = any(expected.value(node, SH.resultMessage) is not None for node in expected_results)
    details = any(expected.value(node, SH.detail) is not None for node in expected_results)
    return isomorphic(
        report_subgraph(actual, actual_root, messages, details),
        report_subgraph(expected, expected_root, messages, details),
    )


def _literal_matches(expected, actual):
    if not isinstance(actual, Literal):
        return False
    try:
        return bool(expected.eq(actual))
    except (TypeError, NotImplementedError):
        # Incomparable literal values are an expected-result mismatch.
        return False


def check_dash_result(report, expected_graph, expanded_data):
    expected = union(expected_graph)
    data = None
    checks = []
    for case in expected.subjects(RDF.type, DASH.GraphValidationTestCase):
        root = expected.value(case, DASH.expectedResult, any=False)
        if root is None:
            raise RuntimeError("GraphValidationTestCase requires dash:expectedResult")
        checks.append(compare_reports(report, expected, root))
    for case in expected.subjects(RDF.type, DASH.InferencingTestCase):
        if data is None:
            from .rdf import load_from_source

            data = union(load_from_source(expanded_data))
        results = list(expected.objects(case, DASH.expectedResult))
        if not results:
            raise RuntimeError("InferencingTestCase requires dash:expectedResult")
        for result in results:
            triple = tuple(
                expected.value(result, p, any=False)
                for p in (RDF.subject, RDF.predicate, RDF.object)
            )
            if None in triple:
                raise RuntimeError("InferencingTestCase requires complete reified triples")
            subject, predicate, value = triple
            if isinstance(value, Literal):
                checks.append(
                    any(
                        _literal_matches(value, actual)
                        for actual in data.objects(subject, predicate)
                    )
                )
            else:
                checks.append(triple in data)
    for case in expected.subjects(RDF.type, DASH.QueryTestCase):
        try:
            matches, _ = evaluate_query_testcase(expected, case)
        except (ValueError, RuntimeError, KeyError, TypeError):
            # DASH query cases intentionally test malformed queries/results.
            # This is the expected-result checker, never a validator fallback.
            matches = False
        checks.append(matches)
    for case in expected.subjects(RDF.type, DASH.FunctionTestCase):
        expression = expected.value(case, DASH.expression, any=False)
        result = expected.value(case, DASH.expectedResult, any=False)
        if expression is None or result is None:
            raise RuntimeError("FunctionTestCase requires dash:expression and dash:expectedResult")
        query = query_prefixes(expected, case) + f"SELECT ({expression} AS ?result) WHERE {{}}"
        snapshot = input_graph(expected)
        actual = Result.parse(
            StringIO(_native.query(snapshot.source, snapshot.format, query)), format="json"
        )
        checks.append([row.asdict().get("result") for row in actual] == [result])
    if not checks:
        raise RuntimeError("Expected graph contains no DASH test cases")
    return all(checks)
