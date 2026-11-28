"""``pyshacl.validator_conformance``: SHT and DASH expected-result checks.

The SHT comparison unfolds both report descriptions into trees, so a blank
node shared by several results (one shape's ``sh:path``) equals separate
copies in the expected graph, as in pySHACL. It is stricter than pySHACL's
focus/value/path keys: every retained field and multiplicity must match.
"""

import logging
from collections import Counter

from rdflib import BNode, Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SH
from rdflib.term import Node

from pyshacl_turbo._native import ValidationFailure
from pyshacl_turbo.conformance import (
    DASH,
    check_dash_result,
    evaluate_query_testcase,
    extract_query_and_expected_result,
)
from pyshacl_turbo.errors import ReportableRuntimeError

SHT = Namespace("http://www.w3.org/ns/shacl-test#")


class ReportTree:
    """A report description unfolded through blank nodes into a comparable value."""

    def __init__(self, graph: Graph, *, messages: bool, details: bool) -> None:
        self.graph = graph
        self.messages = messages
        self.details = details

    def _kept(self, predicate: Node, value: Node) -> bool:
        if predicate == RDF.type and value == RDFS.Resource:
            return False
        if predicate == SH.resultMessage:
            return self.messages
        return predicate != SH.detail or self.details

    def unfold(self, node: Node, path: frozenset[Node] = frozenset()) -> object:
        if not isinstance(node, BNode):
            return node
        if node in path:
            raise ReportableRuntimeError("Cannot compare a cyclic blank-node report description")
        inner = path | {node}
        edges = Counter(
            (predicate, self.unfold(value, inner))
            for _, predicate, value in self.graph.triples((node, None, None))
            if self._kept(predicate, value)
        )
        return frozenset(edges.items())


def compare_sht_report(report: Graph, expected: Graph, expected_root: URIRef | BNode) -> bool:
    """True when the report's unfolded description equals the expected result's."""
    actual_root = report.value(None, RDF.type, SH.ValidationReport, any=False)
    if actual_root is None or report.value(actual_root, SH.conforms) is None:
        raise ReportableRuntimeError("The validation report must declare sh:conforms")
    results = list(expected.objects(expected_root, SH.result))
    messages = any(expected.value(node, SH.resultMessage) is not None for node in results)
    details = any(expected.value(node, SH.detail) is not None for node in results)
    actual = ReportTree(report, messages=messages, details=details).unfold(actual_root)
    wanted = ReportTree(expected, messages=messages, details=details).unfold(expected_root)
    return actual == wanted


def check_sht_result(
    report_graph: Graph | ValidationFailure,
    sht_graph: Graph,
    sht_result_node: URIRef | BNode,
    log: logging.Logger | None = None,
) -> bool:
    """Check one W3C SHACL test-suite outcome, accepting an expected sht:Failure."""
    log = log or logging.getLogger(__name__)
    expected_failure = sht_result_node == SHT.Failure
    if isinstance(report_graph, ValidationFailure):
        if not expected_failure:
            log.error("Validation failed, but the SHT entry does not expect a failure.")
        return expected_failure
    if expected_failure:
        log.error("SHT expects a validation failure, but validation produced a report.")
        return False
    if SH.ValidationReport not in set(sht_graph.objects(sht_result_node, RDF.type)):
        raise ReportableRuntimeError("SHT expected result must have type sh:ValidationReport")
    return compare_sht_report(report_graph, sht_graph, sht_result_node)


__all__ = [
    "DASH",
    "SHT",
    "check_dash_result",
    "check_sht_result",
    "compare_sht_report",
    "evaluate_query_testcase",
    "extract_query_and_expected_result",
]
