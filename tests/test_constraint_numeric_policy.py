"""Numeric declarations use the host conversion and precise public errors."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from pyshacl.errors import ConstraintLoadError as OriginalConstraintLoadError
from rdflib import Graph, Literal, Namespace
from rdflib.compare import isomorphic
from rdflib.namespace import OWL, RDF, RDFS, SH, XSD
from rdflib_turbo import Graph as NativeGraph

EX = Namespace("urn:numeric-policy:")
SYSTEM = {
    (OWL.Class, RDFS.subClassOf, RDFS.Class),
    (OWL.DatatypeProperty, RDFS.subClassOf, RDF.Property),
}


def fixtures(parameter, lexical, graph_type=Graph):
    data, shapes = Graph(), graph_type()
    data.add((EX.focus, EX.p, Literal("")))
    for triple in (
        (EX.shape, RDF.type, SH.PropertyShape),
        (EX.shape, SH.targetNode, EX.focus),
        (EX.shape, SH.path, EX.p),
        (EX.shape, SH[parameter], Literal(lexical, datatype=XSD.integer, normalize=False)),
    ):
        shapes.add(triple)
    if parameter.startswith("qualified"):
        shapes.add((EX.shape, SH.qualifiedValueShape, EX.other))
    return data, shapes


@pytest.mark.parametrize("graph_type", (Graph, NativeGraph))
@pytest.mark.parametrize("codepoint", (0x11BF0, 0x10D40, 0x1E5F1))
@pytest.mark.parametrize(
    "parameter",
    ("minCount", "maxCount", "minLength", "maxLength", "qualifiedMinCount", "qualifiedMaxCount"),
)
def test_numeric_parameters_match_host_errors_and_input_state(parameter, codepoint, graph_type):
    original_data, original_shapes = fixtures(parameter, chr(codepoint))
    data, shapes = fixtures(parameter, chr(codepoint), graph_type)
    before_data, before_shapes = set(data), set(shapes)
    namespaces = dict(shapes.namespaces())
    try:
        expected = pyshacl.validate(original_data, shacl_graph=original_shapes)
    except (TypeError, OriginalConstraintLoadError) as error:
        with pytest.raises((TypeError, turbo.ReportableRuntimeError)) as actual:
            turbo.validate(data, shacl_graph=shapes)
        assert type(actual.value).__name__ == type(error).__name__
        assert str(actual.value) == str(error)
        assert repr(actual.value) == repr(error)
        assert actual.value.args == error.args
        if hasattr(error, "link"):
            assert actual.value.link == error.link
            assert isinstance(actual.value, turbo.ReportableRuntimeError)
    else:
        actual = turbo.validate(data, shacl_graph=shapes)
        assert actual[0] is expected[0]
        assert isomorphic(actual[1], expected[1])
        assert actual[2] == expected[2]
    assert set(data) == set(original_data) == before_data
    assert set(shapes) == set(original_shapes) == before_shapes | SYSTEM
    assert dict(shapes.namespaces()) == namespaces


@pytest.mark.parametrize("lexical", ("0", "٠", "١"))
@pytest.mark.parametrize("parameter", ("minCount", "maxCount", "minLength", "maxLength"))
def test_ascii_and_host_numeric_controls_keep_complete_reports(parameter, lexical):
    original_data, original_shapes = fixtures(parameter, lexical)
    data, shapes = fixtures(parameter, lexical)
    expected = pyshacl.validate(original_data, shacl_graph=original_shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert actual[0] is expected[0]
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
