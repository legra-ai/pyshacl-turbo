"""Report namespaces retain the original core bootstrap and shape binding order."""

from decimal import getcontext

import pyshacl
import pyshacl_turbo
import pytest
from pyshacl.shapes_graph import ShapesGraph
from pyshacl.validator import Validator
from pyshacl_turbo.rdf import decode
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, SH, XSD


def shapes(mode):
    graph = Graph(bind_namespaces=mode if mode in ("core", "rdflib", "none") else "none")
    if mode in ("custom", "conflict"):
        graph.bind("fixture", URIRef("urn:fixture-namespace:"))
        graph.bind("", URIRef("urn:default-namespace:"))
    if mode == "conflict":
        graph.bind("rdf", URIRef("urn:conflicting-rdf:"), replace=True)
        graph.bind("alternate", RDF)
    node = URIRef("urn:S")
    for predicate, value in (
        (RDF.type, SH.PropertyShape),
        (SH.targetNode, URIRef("urn:s")),
        (SH.path, URIRef("urn:p")),
        (SH.minCount, Literal("1", datatype=XSD.integer)),
    ):
        graph.add((node, predicate, value))
    return graph


def observe(module, mode, conforms):
    data, shape_graph = Graph(), shapes(mode)
    data.add((URIRef("urn:s"), URIRef("urn:p" if conforms else "urn:other"), URIRef("urn:o")))
    before = set(data)
    context = getcontext()
    flags, traps = dict(context.flags), dict(context.traps)
    result = module.validate(data, shacl_graph=shape_graph)
    assert dict(context.flags) == flags and dict(context.traps) == traps
    assert set(data) == before
    return result, list(result[1].namespaces()), list(shape_graph.namespaces())


@pytest.mark.parametrize("conforms", [True, False])
def test_public_default_shapes_report_raw_namespace_order_matches_original(
    conforms, record_property
):
    original, expected, expected_shapes = observe(pyshacl, "rdflib", conforms)
    actual, observed, observed_shapes = observe(pyshacl_turbo, "rdflib", conforms)
    record_property("original_namespaces", repr(expected))
    record_property("candidate_namespaces", repr(observed))
    assert actual[0] is original[0] is conforms
    assert isomorphic(actual[1], original[1])
    assert actual[2] == original[2]
    assert observed_shapes == expected_shapes
    assert observed == expected  # The complete raw vector is intentionally unsorted.


@pytest.mark.parametrize("conforms", [True, False])
@pytest.mark.parametrize("mode", ["rdflib", "core", "none", "custom", "conflict"])
def test_report_constructor_matches_original_without_stringification_effects(mode, conforms):
    # Exercise the actual original constructor, before any stringification call.
    prepared = ShapesGraph(shapes(mode))
    before = list(prepared.graph.namespaces())
    node = BNode("result")
    results = [] if conforms else [("Result\n", node, [(node, RDF.type, SH.ValidationResult)])]
    original, _ = Validator.create_validation_report(prepared, conforms, results)
    actual = decode(original.serialize(format="nt"), report=True, _report_conforms=conforms)
    for prefix, namespace in prepared.graph.namespaces():
        actual.bind(prefix, namespace)
    assert list(actual.namespaces()) == list(original.namespaces())
    assert isomorphic(actual, original)
    assert list(prepared.graph.namespaces()) == before


@pytest.mark.parametrize("mode", ["rdflib", "core", "none"])
def test_nonreport_decoder_keeps_its_selected_namespace_bootstrap(mode):
    actual = decode(([], []), _bind_namespaces=mode)
    assert list(actual.namespaces()) == list(Graph(bind_namespaces=mode).namespaces())
