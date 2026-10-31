"""The runtime HTML parser feature preserves copied Graph literal metadata."""

import importlib.metadata
import tomllib
from pathlib import Path
from xml.dom.minidom import DocumentFragment

import pyshacl
import pyshacl_turbo
from packaging.requirements import Requirement
from rdflib import Graph
from rdflib.namespace import SH

ROOT = Path(__file__).resolve().parents[1]


def test_runtime_requires_the_reference_rdflib_html_feature():
    manifest = tomllib.loads((ROOT / "pyproject.toml").read_text())
    for dependencies in (
        manifest["project"]["dependencies"],
        importlib.metadata.requires("pyshacl-turbo"),
    ):
        rdflib = [
            Requirement(value) for value in dependencies if Requirement(value).name == "rdflib"
        ]
        assert len(rdflib) == 1
        assert rdflib[0].extras == {"html"}


def test_graph_html_report_value_preserves_reference_lexical_cache_and_assessment():
    source = '<urn:s> <urn:p> "<p>Hello</p>"^^rdf:HTML .'
    prefix = "@prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>."
    shapes = Graph().parse(
        data="""@prefix sh:<http://www.w3.org/ns/shacl#>.
        <urn:S> a sh:PropertyShape; sh:targetNode <urn:s>;
          sh:path <urn:p>; sh:nodeKind sh:IRI.""",
        format="turtle",
    )
    data = Graph().parse(data=prefix + source, format="turtle")
    before = set(data)
    expected = pyshacl.validate(data, shacl_graph=shapes)
    actual = pyshacl_turbo.validate(data, shacl_graph=shapes)
    assert expected[0] is actual[0] is False
    expected_value = next(expected[1].objects(None, SH.value))
    actual_value = next(actual[1].objects(None, SH.value))
    assert str(actual_value) == str(expected_value) == "<p>Hello"
    assert actual_value.datatype == expected_value.datatype
    assert actual_value.language is expected_value.language is None
    assert actual_value.ill_typed is expected_value.ill_typed is False
    assert type(actual_value.value) is type(expected_value.value) is DocumentFragment
    assert (
        [node.toxml() for node in actual_value.value.childNodes]
        == [node.toxml() for node in expected_value.value.childNodes]
        == ["<p>Hello</p>"]
    )
    assert set(data) == before
    # Report text and document-parser lexical normalization are separate frontiers.
