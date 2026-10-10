"""pySHACL's constraint-path recursion policy, including its depth limit."""

import warnings

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib.compare import isomorphic
from test_compatibility import graph


def capture(engine, data, shapes, **options):
    with warnings.catch_warnings(record=True) as emitted:
        warnings.simplefilter("always")
        result = engine.validate(data, shacl_graph=shapes, **options)
    recursive = [w for w in emitted if w.category.__name__ == "ShapeRecursionWarning"]
    return result, recursive


@pytest.mark.parametrize(
    "definition,data,warning_count",
    [
        ("ex:S sh:node ex:S.", "", 1),
        ("ex:S sh:node ex:T. ex:T sh:node ex:S.", "", 1),
        ('ex:S sh:node ex:S; sh:class ex:Missing; sh:message "missing".', "", 1),
        (
            'ex:S sh:property ex:P. ex:P sh:path ex:p; sh:node ex:S; sh:message "nested".',
            "ex:a ex:p ex:a.",
            1,
        ),
        ("ex:S sh:path ex:p; sh:property ex:S.", "", 0),
        ("ex:S sh:path ex:p; sh:property ex:S.", "ex:a ex:p ex:a.", 1),
        ('ex:S sh:not ex:S; sh:message "negation".', "", 1),
        (
            'ex:S sh:path ex:p; sh:qualifiedValueShape ex:S; sh:qualifiedMinCount 1; sh:message "count".',
            "ex:a ex:p ex:a.",
            1,
        ),
        (
            'ex:S sh:property ex:P. ex:P sh:path ex:p; sh:node ex:S; sh:message "nested".',
            "ex:a ex:p ex:b. ex:b ex:p ex:c. ex:c ex:p ex:d. ex:d ex:p ex:e.",
            1,
        ),
        (
            "ex:S sh:path ex:p; sh:qualifiedValueShape ex:S; sh:qualifiedMinCount 0; sh:qualifiedValueShapesDisjoint true.",
            "ex:a ex:p ex:b. ex:b ex:p ex:c.",
            1,
        ),
    ],
)
def test_recursive_edges_match_reference(definition, data, warning_count):
    shapes = graph("ex:S sh:targetNode ex:a. " + definition)
    expected, reference_warnings = capture(pyshacl, graph(data), shapes)
    assert len(reference_warnings) == warning_count
    actual, native_warnings = capture(turbo, graph(data), shapes)
    assert actual[0] == expected[0]
    assert isomorphic(actual[1], expected[1]), (
        actual[1].serialize(format="turtle"),
        expected[1].serialize(format="turtle"),
    )
    assert len(native_warnings) == len(reference_warnings)
    for warning in native_warnings:
        assert issubclass(warning.category, RuntimeWarning)
        assert "Recursive Shape" in str(warning.message)
        assert "Backing out" in str(warning.message)


@pytest.mark.parametrize("component", ["and", "or", "xone"])
def test_logical_recursion_still_fails_at_reference_depth(component):
    shapes = graph(f"ex:S sh:targetNode ex:a; sh:{component} (ex:S).")
    for engine in (pyshacl, turbo):
        with pytest.raises(RuntimeError, match="Validation path too deep"):
            engine.validate(graph(""), shacl_graph=shapes, max_validation_depth=5)


def test_finite_nesting_obeys_configured_depth():
    shapes = graph(
        'ex:S sh:targetNode ex:a; sh:node ex:T. ex:T sh:node ex:U. ex:U sh:message "end".'
    )
    for engine in (pyshacl, turbo):
        with pytest.raises(RuntimeError, match="Validation path too deep"):
            engine.validate(graph(""), shacl_graph=shapes, max_validation_depth=2)
        assert engine.validate(graph(""), shacl_graph=shapes, max_validation_depth=3)[0]


@pytest.mark.parametrize("entrypoint", ["validate", "shacl_rules"])
@pytest.mark.parametrize("store_input", [False, True])
def test_recursion_warnings_as_errors_do_not_commit_rules(entrypoint, store_input):
    shapes = graph("""
        ex:S sh:targetNode ex:a; sh:rule ex:R.
        ex:R a sh:TripleRule; sh:condition ex:C;
          sh:subject sh:this; sh:predicate ex:derived; sh:object true.
        ex:C sh:node ex:C.
    """)
    data = graph("ex:a ex:p ex:b.")
    if store_input:
        import pyoxigraph

        store = pyoxigraph.Store()
        store.load(input=data.serialize(format="nt"), format=pyoxigraph.RdfFormat.N_TRIPLES)
        data = store
    before = set(data)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(RuntimeWarning, match="Recursive Shape"):
            getattr(turbo, entrypoint)(data, shacl_graph=shapes, advanced=True, inplace=True)
    assert set(data) == before


def test_recursive_rule_condition_emits_warning_and_applies_rule():
    shapes = graph("""
        ex:S sh:targetNode ex:a; sh:rule ex:R.
        ex:R a sh:TripleRule; sh:condition ex:C;
          sh:subject sh:this; sh:predicate ex:derived; sh:object true.
        ex:C sh:node ex:C.
    """)
    expected, reference_warnings = capture(pyshacl, graph(""), shapes, advanced=True)
    actual, native_warnings = capture(turbo, graph(""), shapes, advanced=True)
    assert expected[0] == actual[0]
    assert isomorphic(expected[1], actual[1])
    assert len(native_warnings) == len(reference_warnings) == 1
