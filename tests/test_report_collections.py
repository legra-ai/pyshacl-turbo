"""Complete report graphs and text retain RDF collection path descriptions."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Namespace
from rdflib.compare import isomorphic

EX = Namespace("urn:example:")
PREFIXES = """@prefix ex:<urn:example:>. @prefix sh:<http://www.w3.org/ns/shacl#>.
@prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix xsd:<http://www.w3.org/2001/XMLSchema#>.\n"""
PATHS = [
    "(ex:p ex:q)",
    "[sh:alternativePath (ex:p ex:q)]",
    "(ex:p (ex:q ex:r))",
    "(ex:p [sh:alternativePath (ex:q ex:r)])",
]
NOTES = [
    '("first" "second"@en)',
    '(("plain" "same"^^xsd:string) "français"@fr)',
    '("z" "a" "z")',
]


def report_inputs(*, path="ex:required", note=None):
    data = Graph()
    data.bind("ex", EX)
    annotation = "" if note is None else f"; ex:note {note}"
    shapes = Graph().parse(
        data=PREFIXES
        + f"ex:S sh:targetNode ex:s; sh:property [sh:path {path}; sh:minCount 1 {annotation}].",
        format="turtle",
    )
    return data, shapes


def compare_complete(data, shapes):
    reference_shapes = Graph()
    reference_shapes += shapes
    for prefix, namespace in shapes.namespaces():
        reference_shapes.bind(prefix, namespace)
    before = set(data), set(shapes)
    expected = pyshacl.validate(data, shacl_graph=reference_shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert actual[0] == expected[0] == False
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
    assert (set(data), set(shapes)) == before


@pytest.mark.parametrize("path", PATHS)
def test_complete_path_reports_use_collection_notation(path):
    compare_complete(*report_inputs(path=path))


@pytest.mark.parametrize("note", NOTES)
def test_nested_annotation_collections_keep_order_exact_terms_and_namespaces(note):
    compare_complete(*report_inputs(note=note))


def test_data_list_focus_and_value_descriptions_share_collection_renderer():
    data = Graph().parse(data=PREFIXES + 'ex:s ex:p ("first" "same"^^xsd:string).', format="turtle")
    shapes = Graph().parse(
        data=PREFIXES + "ex:S sh:targetObjectsOf ex:p; sh:class ex:Required.",
        format="turtle",
    )
    compare_complete(data, shapes)


@pytest.mark.parametrize("path", ["_:missingRest", "_:cycle"])
def test_invalid_path_lists_raise_instead_of_returning_a_partial_report(path):
    data = Graph()
    source = (
        PREFIXES
        + f"ex:S sh:targetNode ex:s; sh:property [sh:path {path};sh:minCount 1]."
        + """
    _:missingRest rdf:first ex:p.
    _:missingFirst rdf:first ex:p; rdf:rest _:empty.
    _:cycle rdf:first ex:p; rdf:rest _:cycle."""
    )
    shapes = Graph().parse(data=source, format="turtle")
    for validate in (pyshacl.validate, turbo.validate):
        with pytest.raises((ValueError, pyshacl.errors.ReportableRuntimeError)) as failure:
            validate(data, shacl_graph=shapes)
        assert any(word in str(failure.value).lower() for word in ("list", "path", "collection"))


def test_recursive_annotation_list_fails_before_emitting_a_partial_report():
    source = (
        PREFIXES
        + """ex:S sh:targetNode ex:s; sh:property [sh:path ex:required;
    sh:minCount 1;ex:note _:cycle]. _:cycle rdf:first ex:p; rdf:rest _:cycle."""
    )
    for validate in (pyshacl.validate, turbo.validate):
        with pytest.raises(ValueError, match="(?i)(list|recursive)"):
            validate(Graph(), shacl_graph=Graph().parse(data=source, format="turtle"))


def test_collection_paths_keep_separate_data_and_shape_namespace_bindings():
    data = Graph().parse(data="@prefix ex:<urn:data:>. ex:s ex:marker ex:value.", format="turtle")
    shapes = Graph().parse(
        data="""@prefix ex:<urn:shapes:>. @prefix sh:<http://www.w3.org/ns/shacl#>.
        <urn:Shape> sh:targetNode <urn:data:s>;
        sh:property [sh:path (ex:p ex:q);sh:minCount 1].""",
        format="turtle",
    )
    compare_complete(data, shapes)
