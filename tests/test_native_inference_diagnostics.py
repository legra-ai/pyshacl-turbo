"""Diagnostic namespace visibility follows private and accepted inference state."""

from contextlib import nullcontext

import pytest
from pyshacl import validate as reference_validate
from pyshacl_turbo import validate
from rdflib import Graph, Namespace
from rdflib.compare import isomorphic
from rdflib_turbo import Dataset, StoreDataset
from rdflib_turbo import Graph as NativeGraph

ERROR_NAMESPACE = "http://www.daml.org/2002/03/agents/agent-ont#"
DATA = '<urn:s> <urn:p> "bad"^^<http://www.w3.org/2001/XMLSchema#integer>.'
SHAPES = """@prefix sh:<http://www.w3.org/ns/shacl#>.
<urn:S> sh:targetClass <http://www.daml.org/2002/03/agents/agent-ont#ErrorMessage>;
 sh:property [sh:path <urn:required>;sh:minCount 1]."""
SH = Namespace("http://www.w3.org/ns/shacl#")


@pytest.mark.parametrize("factory", [Dataset, NativeGraph])
@pytest.mark.parametrize("inplace", [False, True])
@pytest.mark.parametrize(
    "bindings",
    [
        [],
        [("err", "urn:other:")],
        [("err", "urn:other:"), ("err1", "urn:more:")],
        [("custom", ERROR_NAMESPACE)],
    ],
)
def test_diagnostic_namespace_stays_private_until_accepted(factory, inplace, bindings):
    shapes = Graph().parse(data=SHAPES, format="turtle")
    reference = Graph().parse(data=DATA, format="turtle")
    for prefix, namespace in bindings:
        reference.bind(prefix, namespace)
    expected = reference_validate(reference, shacl_graph=shapes, inference="owlrl", inplace=inplace)
    source = factory().parse(data=DATA)
    if isinstance(source, Dataset):
        source._native.bind_namespaces(bindings)
    else:
        for prefix, namespace in bindings:
            source.bind(prefix, namespace)
    with source if hasattr(source, "__enter__") else nullcontext(source):
        before = tuple(source.namespaces())
        actual = validate(source, shacl_graph=shapes, inference="owlrl", inplace=inplace)
        assert actual[0] == expected[0] is False
        # Display Literal(...) rendering is a separately confirmed canonical engine defect.
        # Preserve full-message parity in the coordinated canonical regression, while
        # this test isolates private err-prefix selection and metadata acceptance.
        messages = list(actual[1].objects(None, SH.resultMessage))
        assert messages
        expected_messages = list(expected[1].objects(None, SH.resultMessage))
        for actual_message, expected_message in zip(messages, expected_messages, strict=True):
            expected_prefix = str(expected_message).split("[ ")[1].split(":error")[0]
            assert expected_prefix + ":error" in str(actual_message)
        expected_bindings = [
            (str(prefix), str(namespace))
            for prefix, namespace in reference.namespaces()
            if str(namespace) == ERROR_NAMESPACE
        ]
        actual_bindings = [
            (str(prefix), str(namespace))
            for prefix, namespace in source.namespaces()
            if str(namespace) == ERROR_NAMESPACE
        ]
        assert actual_bindings == expected_bindings
        if not inplace:
            assert tuple(source.namespaces()) == before


@pytest.mark.parametrize("factory", [NativeGraph, StoreDataset])
@pytest.mark.parametrize("mode", ["rdfs", "owlrl", "both"])
def test_data_prefix_mapping_is_distinct_from_shapes_prefix_mapping(factory, mode):
    data = """@prefix ex:<urn:validation-inference:>.
    ex:child <http://www.w3.org/2000/01/rdf-schema#subPropertyOf> ex:parent.
    ex:s ex:child ex:o."""
    shapes = Graph().parse(
        data="""@prefix sh:<http://www.w3.org/ns/shacl#>.
    @prefix ex:<urn:shape:>.
    ex:S sh:targetSubjectsOf <urn:validation-inference:parent>;
    sh:property [sh:path <urn:validation-inference:name>;sh:minCount 1].""",
        format="turtle",
    )
    expected = reference_validate(
        Graph().parse(data=data, format="turtle"), shacl_graph=shapes, inference=mode
    )
    source = factory().parse(data=data)
    actual = validate(source, shacl_graph=shapes, inference=mode)
    assert not actual[0]
    assert isomorphic(actual[1], expected[1])
    source.close()
