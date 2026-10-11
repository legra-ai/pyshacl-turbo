"""Compare public calls directly, without the upstream redirection adapter."""

from collections import UserList

import pyshacl
import pyshacl_turbo as turbo
import pytest
from pyshacl.errors import ReportableRuntimeError as ReferenceRuntimeError
from rdflib import Dataset, Graph, URIRef
from rdflib.compare import isomorphic

PREFIXES = """
@prefix ex: <urn:example:> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
"""


def graph(text=""):
    return Graph().parse(data=PREFIXES + text, format="turtle")


def triples(source):
    """RDFLib 7.6 Dataset iteration returns quads; compare the explicit union."""
    result = Graph()
    for triple in source.triples((None, None, None)):
        result.add(triple)
    return result


@pytest.mark.parametrize("container", [list, tuple, UserList])
@pytest.mark.parametrize("entrypoint", ["validate_each", "validate"])
def test_independent_validation_returns_indexed_results(container, entrypoint):
    data = container([graph(), graph("ex:s ex:p 1.")])
    shapes = graph("ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1.")
    options = {"shacl_graph": shapes}
    if entrypoint == "validate":
        options["multi_data_graphs_mode"] = "validate_each"
    expected = getattr(pyshacl, entrypoint)(data, **options)
    actual = getattr(turbo, entrypoint)(data, **options)

    assert type(actual) is type(expected) is dict
    assert list(actual) == list(expected) == [0, 1]
    for index in expected:
        assert actual[index][0] is expected[index][0]
        assert isomorphic(actual[index][1], expected[index][1])


@pytest.mark.parametrize("value", [graph(), "", b"", [], (), UserList()])
def test_validate_each_rejects_invalid_or_empty_input_with_reference_error(value):
    with pytest.raises(ReferenceRuntimeError) as expected:
        pyshacl.validate_each(value)
    with pytest.raises(turbo.ReportableRuntimeError) as actual:
        turbo.validate_each(value)
    assert str(actual.value) == str(expected.value)


@pytest.mark.parametrize("entrypoint", ["validate", "validate_each", "shacl_rules"])
def test_public_entrypoints_accept_reference_positional_arguments(entrypoint):
    data = [graph()] if entrypoint == "validate_each" else graph()
    expected = getattr(pyshacl, entrypoint)(data, "legacy positional argument", shacl_graph=graph())
    actual = getattr(turbo, entrypoint)(data, "legacy positional argument", shacl_graph=graph())
    if entrypoint == "shacl_rules":
        assert isomorphic(actual, expected)
    elif entrypoint == "validate_each":
        assert type(actual) is type(expected)
        assert actual[0][0] is expected[0][0]
    else:
        assert actual[0] is expected[0]


def test_combined_validation_accepts_a_general_sequence():
    shapes = graph("ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1.")
    data = UserList([graph().serialize(), graph("ex:s ex:p 1.").serialize()])
    expected = pyshacl.validate(data, shacl_graph=shapes, data_graph_format="turtle")
    actual = turbo.validate(data, shacl_graph=shapes, data_graph_format="turtle")
    assert actual[0] is expected[0] is True
    assert isomorphic(actual[1], expected[1])


RULE_SHAPES = """
ex:First sh:targetClass ex:Person;
  sh:rule [ a sh:TripleRule; sh:subject sh:this; sh:predicate ex:first; sh:object true ].
ex:Second sh:targetNode ex:b;
  sh:rule [ a sh:TripleRule; sh:subject sh:this; sh:predicate ex:second; sh:object true ].
"""


@pytest.mark.parametrize(
    "options",
    [
        {"focus_nodes": ["urn:example:a"]},
        {"use_shapes": ["urn:example:First"]},
        {"focus_nodes": ["urn:example:untargeted"], "use_shapes": ["urn:example:First"]},
        {"focus_nodes": ["ex:a"], "use_shapes": ["ex:Second"]},
    ],
)
@pytest.mark.parametrize("entrypoint", ["shacl_rules", "validate"])
def test_rules_respect_shape_and_focus_selection(options, entrypoint):
    data = "ex:a a ex:Person. ex:b a ex:Person."
    expected_data, actual_data = graph(data), graph(data)
    shapes = graph(RULE_SHAPES)
    kwargs = {"shacl_graph": shapes, "inplace": True, **options}
    if entrypoint == "validate":
        kwargs["advanced"] = True
    getattr(pyshacl, entrypoint)(expected_data, **kwargs)
    getattr(turbo, entrypoint)(actual_data, **kwargs)
    assert isomorphic(actual_data, expected_data), {
        "missing": sorted(map(str, set(expected_data) - set(actual_data))),
        "extra": sorted(map(str, set(actual_data) - set(expected_data))),
    }


@pytest.mark.parametrize("rdf_format", [None, "turtle", "nt", "json-ld"])
def test_rule_expansion_serialization_options(rdf_format):
    options = {"shacl_graph": graph(RULE_SHAPES), "serialize_expanded_graph": True}
    if rdf_format is not None:
        options["serialize_expanded_graph_format"] = rdf_format
    data = graph("ex:a a ex:Person.")
    expected = pyshacl.shacl_rules(data, **options)
    actual = turbo.shacl_rules(data, **options)
    assert isinstance(actual, str) and isinstance(expected, str)
    actual_graph = Dataset(default_union=True).parse(data=actual, format=rdf_format or "trig")
    expected_graph = Dataset(default_union=True).parse(data=expected, format=rdf_format or "trig")
    assert isomorphic(triples(actual_graph), triples(expected_graph))


@pytest.mark.parametrize("inplace", [False, True])
def test_rule_expansion_preserves_graph_identifier_and_default_serialization_context(inplace):
    data = Graph(identifier=URIRef("urn:input")).parse(
        data=PREFIXES + "ex:a a ex:Person.", format="turtle"
    )
    options = {"shacl_graph": graph(RULE_SHAPES), "inplace": inplace}
    expected = pyshacl.shacl_rules(data, **options)
    actual = turbo.shacl_rules(data, **options)
    # The reference wrapper exposes a string; RDFLib exposes an RDF term.
    assert str(actual.identifier) == str(expected.identifier) == str(data.identifier)
    expected_text = pyshacl.shacl_rules(data, serialize_expanded_graph=True, **options)
    actual_text = turbo.shacl_rules(data, serialize_expanded_graph=True, **options)
    expected_dataset = Dataset().parse(data=expected_text, format="trig")
    actual_dataset = Dataset().parse(data=actual_text, format="trig")
    assert set(actual_dataset.quads()) == set(expected_dataset.quads())


def test_native_rule_output_can_serialize_rdfxml_despite_reference_wrapper_bug():
    options = {
        "shacl_graph": graph(RULE_SHAPES),
        "serialize_expanded_graph": True,
        "serialize_expanded_graph_format": "xml",
    }
    data = graph("ex:a a ex:Person.")
    with pytest.raises(TypeError, match="subjects.*missing"):
        pyshacl.shacl_rules(data, **options)
    result = turbo.shacl_rules(data, **options)
    expected_graph = pyshacl.shacl_rules(data, shacl_graph=options["shacl_graph"])
    assert isomorphic(Graph().parse(data=result, format="xml"), triples(expected_graph))


@pytest.mark.parametrize("severity", ["Violation", "Warning", "Info"])
def test_human_report_component_heading_matches_reference(severity):
    shapes = graph(
        f"ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1; sh:severity sh:{severity}."
    )
    expected = pyshacl.validate(graph(), shacl_graph=shapes)
    actual = turbo.validate(graph(), shacl_graph=shapes)
    assert actual[2] == expected[2]


def test_reportable_runtime_error_preserves_reference_public_attributes():
    from pyshacl_turbo.errors import ReportableRuntimeError

    expected = ReferenceRuntimeError("invalid request")
    actual = ReportableRuntimeError("invalid request")
    assert ReportableRuntimeError is turbo.ReportableRuntimeError
    assert actual.message == expected.message
    assert actual.args == expected.args
    assert repr(actual) == repr(expected)
    assert str(actual) == str(expected)


@pytest.mark.parametrize("rdf_format", ["json-ld", "nquads"])
def test_context_aware_rule_serialization_preserves_named_graph(rdf_format):
    data = Graph(identifier=URIRef("urn:input")).parse(
        data=PREFIXES + "ex:a a ex:Person.", format="turtle"
    )
    options = {
        "shacl_graph": graph(RULE_SHAPES),
        "serialize_expanded_graph": True,
        "serialize_expanded_graph_format": rdf_format,
    }
    expected = Dataset().parse(data=pyshacl.shacl_rules(data, **options), format=rdf_format)
    actual = Dataset().parse(data=turbo.shacl_rules(data, **options), format=rdf_format)
    assert set(actual.quads()) == set(expected.quads())


def test_public_version_matches_installed_distribution():
    from importlib.metadata import version

    assert turbo.__version__ == version("pyshacl-turbo")


@pytest.mark.parametrize("adapter", ["graph", "store"])
def test_report_uses_each_source_graphs_own_namespaces(adapter):
    body = "@prefix data: <urn:example:> . data:a data:p 1."
    if adapter == "store":
        from pyoxigraph import RdfFormat, Store

        data = Store()
        data.load(input=body, format=RdfFormat.TURTLE)
    else:
        data = Graph().parse(data=body, format="turtle")
    shapes = graph("ex:S sh:targetNode ex:a; sh:path ex:missing; sh:minCount 1.")
    expected = pyshacl.validate(data, shacl_graph=shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
