"""Unknown scalar functions produce SPARQL expression errors, not query errors."""

import pytest
from test_compatibility import compare, graph


@pytest.mark.parametrize(
    "body,conforms",
    [
        ("FILTER(<urn:undefined>($this))", True),
        ("BIND(<urn:undefined>($this) AS ?result) FILTER(!BOUND(?result))", False),
        ("FILTER(COALESCE(<urn:undefined>($this), true))", False),
        ("FILTER(true || <urn:undefined>($this))", False),
        ("FILTER(false && <urn:undefined>($this))", True),
        ("{ FILTER(<urn:undefined>($this)) } UNION { FILTER(true) }", False),
        ("FILTER(COALESCE(<urn:undefined>(42), true))", False),
    ],
)
def test_undefined_function_expression_semantics(body, conforms):
    shapes = graph(f"""
        ex:S sh:targetNode ex:a; sh:sparql ex:C.
        ex:C sh:message "result"; sh:select "SELECT $this WHERE {{ {body} }}".
    """)
    assert compare(graph(""), shapes)[0] is conforms
