"""Empty descriptions retain the reference's single interior space."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Graph
from rdflib.compare import isomorphic

PREFIXES = """@prefix ex:<urn:example:>. @prefix sh:<http://www.w3.org/ns/shacl#>.
@prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>.\n"""
CASES = {
    "annotation": (
        "",
        "ex:S sh:targetNode ex:s;sh:property [sh:path ex:p;sh:minCount 1;ex:note []].",
    ),
    "list-item": (
        "",
        "ex:S sh:targetNode ex:s;sh:property [sh:path ex:p;sh:minCount 1;ex:note ([])].",
    ),
    "reused-empty-item": (
        "",
        "ex:S sh:targetNode ex:s;sh:property [sh:path ex:p;sh:minCount 1;ex:note (_:empty _:empty)].",
    ),
    "focus": ("", "ex:S sh:targetNode _:empty;sh:class ex:Required."),
    "value": (
        "ex:s ex:p [].",
        "ex:S sh:targetNode ex:s;sh:property [sh:path ex:p;sh:class ex:Required].",
    ),
    "nonempty-control": (
        "",
        'ex:S sh:targetNode ex:s;sh:property [sh:path ex:p;sh:minCount 1;ex:note [ex:p "value"]].',
    ),
    "shared-depth-control": (
        "",
        """ex:S sh:targetNode ex:s;sh:property [sh:path ex:p;sh:minCount 1;ex:note _:head].
        _:head ex:a _:shared;ex:z _:chain0. _:chain0 ex:next _:chain1.
        _:chain1 ex:next _:shared. _:shared ex:next _:tail0. _:tail0 ex:next _:tail1.
        _:tail1 ex:value "end".""",
    ),
}


def inputs(case):
    data, shapes = CASES[case]
    return (
        Graph().parse(data=PREFIXES + data, format="turtle"),
        Graph().parse(data=PREFIXES + shapes, format="turtle"),
    )


def compare_complete(case):
    data, shapes = inputs(case)
    reference_data, reference_shapes = inputs(case)
    before = set(data), set(shapes), tuple(data.namespaces()), tuple(shapes.namespaces())
    original_shapes_before = set(reference_shapes)
    expected = pyshacl.validate(reference_data, shacl_graph=reference_shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert actual[0] == expected[0] == False
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
    assert original_shapes_before <= set(reference_shapes)
    expected_shapes = before[1] | (set(reference_shapes) - original_shapes_before)
    assert (set(data), set(shapes), tuple(data.namespaces()), tuple(shapes.namespaces())) == (
        before[0],
        expected_shapes,
        before[2],
        before[3],
    )


@pytest.mark.parametrize("case", CASES)
def test_complete_report_empty_blank_format_and_unchanged_controls(case):
    compare_complete(case)
