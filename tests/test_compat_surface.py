"""``pyshacl_turbo.compat`` mirrors pySHACL 0.40.2's public names at their paths (ADR 0049)."""

import importlib
import logging
from pathlib import Path, PurePath

import pyshacl
import pyshacl_turbo
import pytest
from pyshacl_turbo import _native
from pyshacl_turbo.compat import validator_conformance as conformance
from pyshacl_turbo.compat.rdfutil.load import path_from_uri
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SH

assert not hasattr(pyshacl, "__turbo__"), "conftest must turn the alias off"

MIRRORED = [
    "",
    ".entrypoints",
    ".errors",
    ".rdfutil",
    ".rdfutil.load",
    ".graph_abstraction",
    ".validator_conformance",
    ".validator",
    ".shape",
    ".shapes_graph",
    ".rule_expand_runner",
    ".cli",
    ".cli_rules",
]
TURBO_ONLY = {".validator_conformance": {"SHT", "compare_sht_report"}}


@pytest.mark.parametrize("path", MIRRORED)
def test_every_compat_name_exists_at_the_reference_path(path):
    mirror = importlib.import_module("pyshacl_turbo.compat" + path)
    reference = importlib.import_module("pyshacl" + path)
    names = set(mirror.__all__) - TURBO_ONLY.get(path, set())
    assert names <= set(dir(reference)), names - set(dir(reference))
    for name in names:
        assert getattr(mirror, name) is not None


def test_the_reference_top_level_names_are_all_mirrored():
    from pyshacl_turbo import compat

    assert set(pyshacl.__all__) <= set(compat.__all__)
    assert compat.__version__ == pyshacl.__version__


@pytest.mark.parametrize(
    "name",
    [
        "ReportableRuntimeError",
        "ShapeLoadError",
        "ConstraintLoadError",
        "RuleLoadError",
        "ValidationWarning",
        "ShapeRecursionWarning",
        "ConstraintLoadWarning",
    ],
)
def test_error_hierarchies_match_the_reference(name):
    from pyshacl import errors as reference
    from pyshacl_turbo.compat import errors

    def bases(cls):
        return [base.__name__ for base in cls.__mro__]

    assert bases(getattr(errors, name)) == bases(getattr(reference, name))


def test_rule_load_error_matches_the_reference_contract():
    from pyshacl import errors as reference
    from pyshacl_turbo.compat.errors import RuleLoadError

    ours, theirs = (
        RuleLoadError("bad rule", "urn:link"),
        reference.RuleLoadError("bad rule", "urn:link"),
    )
    assert ours.args == theirs.args and str(ours) == str(theirs)
    assert repr(ours) == "RuleLoadError: " + str(ours)


@pytest.mark.parametrize(
    ("uri", "relative"),
    [
        ("file:///tmp/a%20b.ttl", None),
        ("file://localhost/tmp/x.ttl", None),
        ("file:////server/share/x.ttl", None),
        ("file:///C|/dir/x.ttl", None),
        ("file:relative/x.ttl", PurePath("/base")),
    ],
)
def test_path_from_uri_matches_the_reference(uri, relative):
    from pyshacl.rdfutil.load import path_from_uri as reference

    assert path_from_uri(uri, relative_to=relative) == reference(uri, relative_to=relative)
    assert isinstance(path_from_uri(URIRef(uri)), Path)


def test_path_from_uri_rejects_other_schemes():
    with pytest.raises(ValueError, match="does not start with 'file:'"):
        path_from_uri("http://example.org/x.ttl")


def test_has_oxigraph_reports_the_optional_store_support():
    from pyshacl.graph_abstraction import has_oxigraph as reference
    from pyshacl_turbo.compat.graph_abstraction import has_oxigraph

    assert has_oxigraph is reference


EX = "urn:sht:"
EXPECTED = f"""
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<{EX}case> <{EX}result> [
    a sh:ValidationReport ; sh:conforms false ;
    sh:result [ a sh:ValidationResult ; sh:focusNode <{EX}a> ;
                sh:resultPath [ sh:inversePath <{EX}p> ] ; sh:resultSeverity sh:Violation ] ;
    sh:result [ a sh:ValidationResult ; sh:focusNode <{EX}b> ;
                sh:resultPath [ sh:inversePath <{EX}p> ] ; sh:resultSeverity sh:Violation ]
] .
"""


def expected():
    graph = Graph().parse(data=EXPECTED, format="turtle")
    return graph, graph.value(URIRef(EX + "case"), URIRef(EX + "result"))


def report(*, shared=True, focus=("a", "b"), message=None, detail=False, resource=True):
    graph = Graph()
    root = BNode()
    graph.add((root, RDF.type, SH.ValidationReport))
    graph.add((root, SH.conforms, Literal(False)))
    if resource:
        graph.add((root, RDF.type, RDFS.Resource))
    path = BNode()
    graph.add((path, SH.inversePath, URIRef(EX + "p")))
    for name in focus:
        result = BNode()
        graph.add((root, SH.result, result))
        graph.add((result, RDF.type, SH.ValidationResult))
        graph.add((result, SH.focusNode, URIRef(EX + name)))
        graph.add((result, SH.resultSeverity, SH.Violation))
        if not shared:
            path = BNode()
            graph.add((path, SH.inversePath, URIRef(EX + "p")))
        graph.add((result, SH.resultPath, path))
        if message:
            graph.add((result, SH.resultMessage, Literal(message)))
        if detail:
            nested = BNode()
            graph.add((result, SH.detail, nested))
            graph.add((nested, SH.focusNode, URIRef(EX + "x")))
    return graph


@pytest.mark.parametrize("shared", [True, False])
def test_sht_reports_compare_unfolded_through_blank_nodes(shared):
    sht, node = expected()
    assert conformance.check_sht_result(report(shared=shared, message="m", detail=True), sht, node)


def test_sht_reports_reject_a_missing_result():
    sht, node = expected()
    assert not conformance.check_sht_result(report(focus=("a",)), sht, node)


def test_sht_reports_keep_messages_and_details_when_expected():
    sht, node = expected()
    for result in list(sht.objects(node, SH.result)):
        sht.add((result, SH.resultMessage, Literal("m")))
    assert conformance.check_sht_result(report(message="m"), sht, node)
    assert not conformance.check_sht_result(report(message="other"), sht, node)
    for result in list(sht.objects(node, SH.result)):
        sht.add((result, SH.detail, BNode()))
    assert not conformance.check_sht_result(report(message="m"), sht, node)


def test_sht_failures_are_expected_or_reported(caplog):
    sht, node = expected()
    failure = _native.ValidationFailure("boom")
    assert conformance.check_sht_result(failure, sht, conformance.SHT.Failure)
    with caplog.at_level(logging.ERROR):
        assert not conformance.check_sht_result(failure, sht, node)
        assert not conformance.check_sht_result(report(), sht, conformance.SHT.Failure, log=None)
    assert (
        "does not expect a failure" in caplog.text and "expects a validation failure" in caplog.text
    )


def test_sht_expected_results_must_be_reports():
    sht, node = expected()
    sht.remove((node, RDF.type, SH.ValidationReport))
    with pytest.raises(pyshacl_turbo.ReportableRuntimeError, match="sh:ValidationReport"):
        conformance.check_sht_result(report(), sht, node)


def test_sht_actual_reports_must_declare_conformance():
    sht, node = expected()
    graph = report()
    graph.remove((None, SH.conforms, None))
    with pytest.raises(pyshacl_turbo.ReportableRuntimeError, match="sh:conforms"):
        conformance.compare_sht_report(graph, sht, node)
    with pytest.raises(pyshacl_turbo.ReportableRuntimeError, match="sh:conforms"):
        conformance.compare_sht_report(Graph(), sht, node)


def test_sht_cyclic_descriptions_are_rejected():
    sht, node = expected()
    graph = report()
    root = graph.value(None, RDF.type, SH.ValidationReport)
    loop = BNode()
    graph.add((root, URIRef(EX + "loop"), loop))
    graph.add((loop, URIRef(EX + "loop"), loop))
    with pytest.raises(pyshacl_turbo.ReportableRuntimeError, match="cyclic"):
        conformance.compare_sht_report(graph, sht, node)
