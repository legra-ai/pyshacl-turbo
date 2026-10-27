"""Typed shape declaration failures match original public exceptions."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from pyshacl.errors import ShapeLoadError as ReferenceError
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SH
from rdflib_turbo import Graph as NativeGraph


def malformed(kind, graph_type=Graph):
    graph = graph_type()
    node = URIRef("urn:shape-error:shape")
    graph.add((node, RDF.type, SH.NodeShape if kind == "node_path" else SH.PropertyShape))
    graph.add((node, SH.targetNode, URIRef("urn:shape-error:focus")))
    if kind != "missing_path":
        graph.add((node, SH.path, Literal("bad") if kind == "literal_path" else URIRef("urn:p")))
    if kind == "multiple_paths":
        graph.add((node, SH.path, URIRef("urn:q")))
    return graph


@pytest.mark.parametrize("kind", ("literal_path", "node_path", "missing_path", "multiple_paths"))
@pytest.mark.parametrize("graph_type", (Graph, NativeGraph))
@pytest.mark.parametrize("boundary", ("validate", "compile"))
def test_shape_load_failures_preserve_type_message_and_link(kind, graph_type, boundary):
    original_shapes = malformed(kind)
    turbo_shapes = malformed(kind, graph_type)
    with pytest.raises(ReferenceError) as expected:
        pyshacl.validate(Graph(), shacl_graph=original_shapes)
    with pytest.raises(turbo.ReportableRuntimeError) as actual:
        if boundary == "validate":
            turbo.validate(Graph(), shacl_graph=turbo_shapes)
        else:
            turbo.CompiledShapes(turbo_shapes)
    from pyshacl_turbo.errors import ShapeLoadError

    assert type(actual.value) is ShapeLoadError
    assert actual.value.message == expected.value.message
    assert actual.value.link == expected.value.link
    assert actual.value.args == expected.value.args
    assert str(actual.value) == str(expected.value)
    assert repr(actual.value) == repr(expected.value)


def test_unrelated_parser_and_unsupported_errors_are_not_shape_errors():
    with pytest.raises(ValueError) as parser:
        turbo.CompiledShapes(b"this is not RDF", shacl_graph_format="nt")
    assert not isinstance(parser.value, turbo.ReportableRuntimeError)
    with pytest.raises(NotImplementedError):
        turbo.validate(Graph(), shacl_graph=Graph(), js=True)
