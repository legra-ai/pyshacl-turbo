"""Public inference options preserve the original error and alias contracts."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from pyshacl.errors import ReportableRuntimeError as ReferenceError
from rdflib import Graph, Namespace
from rdflib.compare import isomorphic
from rdflib_turbo import Dataset as NativeDataset
from rdflib_turbo import Graph as NativeGraph

EX = Namespace("urn:inference-option:")
SH = Namespace("http://www.w3.org/ns/shacl#")


def shapes():
    graph = Graph()
    graph.add((EX.shape, SH.targetNode, EX.focus))
    graph.add((EX.shape, SH["class"], EX.Required))
    return graph


@pytest.mark.parametrize("option", ("bad", "RDFS", 123, True))
@pytest.mark.parametrize("data_type", (Graph, NativeGraph, NativeDataset))
def test_validate_unknown_inference_matches_original(option, data_type):
    expected_shapes = shapes()
    actual_shapes = shapes()
    with pytest.raises(ReferenceError) as expected:
        pyshacl.validate(Graph(), shacl_graph=expected_shapes, inference=option)
    with pytest.raises(turbo.ReportableRuntimeError) as actual:
        turbo.validate(data_type(), shacl_graph=actual_shapes, inference=option)
    assert type(actual.value) is turbo.ReportableRuntimeError
    assert str(actual.value) == str(expected.value)
    assert actual.value.args == expected.value.args


@pytest.mark.parametrize("option", ("bad", "RDFS", 123, True))
def test_compiled_native_unknown_inference_uses_public_error(option):
    with pytest.raises(ReferenceError) as expected:
        pyshacl.validate(Graph(), shacl_graph=shapes(), inference=option)
    compiled = turbo.CompiledShapes(shapes())
    with pytest.raises(turbo.ReportableRuntimeError) as actual:
        compiled.validate(NativeDataset(), inference=option)
    assert type(actual.value) is turbo.ReportableRuntimeError
    assert str(actual.value) == str(expected.value)


@pytest.mark.parametrize("option", ("", False, 0, [], {}))
@pytest.mark.parametrize("data_type", (Graph, NativeGraph, NativeDataset))
def test_falsey_inference_is_disabled_like_original(option, data_type):
    expected_shapes = shapes()
    actual_shapes = shapes()
    expected = pyshacl.validate(Graph(), shacl_graph=expected_shapes, inference=option)
    actual = turbo.validate(data_type(), shacl_graph=actual_shapes, inference=option)
    assert actual[0] is expected[0] is False
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]


@pytest.mark.parametrize("option", ("all", "rdfsowlrl"))
@pytest.mark.parametrize("data_type", (Graph, NativeDataset))
def test_inference_aliases_keep_full_report(option, data_type):
    expected_shapes = shapes()
    actual_shapes = shapes()
    expected = pyshacl.validate(Graph(), shacl_graph=expected_shapes, inference=option)
    actual = turbo.validate(data_type(), shacl_graph=actual_shapes, inference=option)
    assert actual[0] is expected[0] is False
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]


def test_compiled_native_source_contract_precedes_inference_normalization():
    program = turbo.CompiledShapes(shapes())
    with pytest.raises(ValueError, match="data_graph_format is unavailable for a native source"):
        program.validate(NativeDataset(), data_graph_format="nt", inference="bad")
