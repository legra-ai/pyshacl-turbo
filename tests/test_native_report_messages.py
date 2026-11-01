"""Released provider upgrades must preserve complete public validation reports."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib.compare import isomorphic
from test_compatibility import graph


@pytest.mark.parametrize(
    "data,constraint",
    [
        ('ex:s ex:p "literal".', "sh:nodeKind sh:IRI"),
        ('ex:s ex:p "hello"@en.', 'sh:languageIn ("fr")'),
        ("ex:s ex:p ex:value.", "sh:expression ex:notTrue"),
        (
            "ex:s ex:p ex:value.",
            (
                'sh:sparql [sh:select "SELECT $this ?value WHERE {$this '
                '<https://example.com/p> ?value}"]'
            ),
        ),
    ],
    ids=["node-kind", "language-list", "expression", "select-without-message"],
)
def test_provider_default_messages_match_complete_reference_report(data, constraint):
    shapes_body = f"ex:S sh:targetNode ex:s; sh:path ex:p; {constraint}."
    expected = pyshacl.validate(graph(data), shacl_graph=graph(shapes_body), advanced=True)
    actual = turbo.validate(graph(data), shacl_graph=graph(shapes_body), advanced=True)
    assert actual[0] is expected[0] is False
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
    assert list(actual[1].namespaces()) == list(expected[1].namespaces())
