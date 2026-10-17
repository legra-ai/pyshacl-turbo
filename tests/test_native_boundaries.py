"""Exercise the native text and term-record APIs, including rejected boundaries."""

import json

import pyshacl_turbo as turbo
import pytest
from pyshacl_turbo import _native
from rdflib import Graph


@pytest.mark.parametrize("text", ["--02-29", "--02-29Z", "--02-29+14:00", "--02-29-14:00"])
def test_month_day_allows_february_29_without_a_year(text):
    data = Graph().parse(
        data=f'<urn:s> <urn:p> "{text}"^^<http://www.w3.org/2001/XMLSchema#gMonthDay> .',
        format="nt",
    )
    shapes = Graph().parse(
        data="@prefix sh: <http://www.w3.org/ns/shacl#>. <urn:S> sh:targetNode <urn:s>; sh:path <urn:p>; sh:datatype <http://www.w3.org/2001/XMLSchema#gMonthDay>.",
        format="turtle",
    )
    assert turbo.validate(data, shacl_graph=shapes)[0]


@pytest.mark.parametrize(
    "text",
    [
        "--02-30",
        "--04-31",
        "--13-01",
        "--00-01",
        "--02-00",
        "02-29",
        "--2-29",
        "--02-29+14:01",
        "--02-29+15:00",
    ],
)
def test_month_day_rejects_invalid_calendar_dates_and_timezones(text):
    data = Graph().parse(
        data=f'<urn:s> <urn:p> "{text}"^^<http://www.w3.org/2001/XMLSchema#gMonthDay> .',
        format="nt",
    )
    shapes = Graph().parse(
        data="@prefix sh: <http://www.w3.org/ns/shacl#>. <urn:S> sh:targetNode <urn:s>; sh:path <urn:p>; sh:datatype <http://www.w3.org/2001/XMLSchema#gMonthDay>.",
        format="turtle",
    )
    assert not turbo.validate(data, shacl_graph=shapes)[0]


@pytest.mark.parametrize(
    "record",
    [
        (0, "not an IRI", None, None),
        (1, "bad node!", None, None),
        (2, "text", None, "bad language!"),
        (2, "text", "bad datatype", None),
        (2, "text", "urn:datatype", "en"),
        (99, "text", None, None),
    ],
)
def test_native_batch_rejects_malformed_terms(record):
    batch = ([record], [])
    with pytest.raises(ValueError):
        _native.additions(batch, "terms", batch)


@pytest.mark.parametrize("quad", [(5, 1, 2, None), (0, 5, 2, None), (0, 1, 5, None), (0, 1, 2, 5)])
def test_native_batch_validates_every_term_index(quad):
    records = [(0, "urn:s", None, None), (0, "urn:p", None, None), (2, "text", None, None)]
    with pytest.raises(ValueError, match="Invalid RDF term index"):
        _native.additions((records, [quad]), "terms", ([], []))


def test_native_text_additions_and_inference_return_rdf_text():
    before = '<urn:s> <urn:p> "old" .'
    after = before + '\n<urn:s> <urn:p> "new" .'
    delta = _native.additions(before, "nt", after)
    assert '"new"' in delta and '"old"' not in delta
    inferred = _native.infer(
        "<urn:C> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <urn:D> . <urn:x> a <urn:C>.",
        "turtle",
        "rdfs",
        "urn:inferred",
    )
    assert "<urn:x>" in inferred and "<urn:inferred>" in inferred
    with pytest.raises(ValueError):
        _native.infer("", "turtle", "rdfs", "invalid IRI")
    assert (
        json.loads(_native.query('_:s <urn:p> "x".', "nt", "SELECT ?s WHERE { ?s ?p ?o }"))[
            "results"
        ]["bindings"][0]["s"]["type"]
        == "bnode"
    )
    with pytest.raises(ValueError, match="SELECT or ASK"):
        _native.query("", "nt", "CONSTRUCT {} WHERE {}")


@pytest.mark.parametrize(
    "format,source",
    [
        ("n3", '<urn:s> <urn:p> "é" .'),
        ("json-ld", '{"@id":"urn:s", "urn:p":{"@value":"é"}}'),
        ("jsonld", '{"@id":"urn:s", "urn:p":{"@value":"é"}}'),
    ],
)
def test_native_parser_handles_all_supported_text_formats(format, source):
    output, _ = _native.parse_rdf(source, format, None)
    assert len(Graph().parse(data=output, format="nt")) == 1


def test_native_parser_rejects_invalid_formats_and_bases():
    with pytest.raises(NotImplementedError):
        _native.parse_rdf("", "unknown", None)
    with pytest.raises(ValueError):
        _native.parse_rdf("", "turtle", "invalid IRI")


def test_legacy_native_validation_and_expansion_keep_text_outputs_and_validate_options():
    compiled = _native.CompiledShapes("", "turtle", None, False, True, [])
    assert compiled.shape_nodes() == []
    arguments = {
        "source": "",
        "rdf_format": "nt",
        "base": None,
        "iterate_rules": False,
        "max_rule_iterations": 100,
        "max_validation_depth": 15,
        "include_data": True,
        "allow_infos": False,
        "allow_warnings": False,
        "abort_on_first": False,
        "focus_nodes": [],
        "use_shapes": [],
        "namespaces": [],
    }
    conforms, report, text, expanded, warnings = compiled.validate(**arguments)
    assert conforms and isinstance(report, str) and expanded == "" and not warnings
    assert "Conforms: True" in text
    for name in ("focus_nodes", "use_shapes"):
        with pytest.raises(ValueError):
            compiled.validate(**(arguments | {name: ["invalid IRI"]}))
    expansion = {
        "source": "",
        "rdf_format": "nt",
        "base": None,
        "iterate_rules": False,
        "max_rule_iterations": 100,
        "max_validation_depth": 15,
        "focus_nodes": [],
        "use_shapes": [],
        "additions_only": False,
    }
    assert compiled.expand(**expansion) == ("", [])
    assert compiled.expand(**(expansion | {"additions_only": True})) == ("", [])
    for name in ("focus_nodes", "use_shapes"):
        with pytest.raises(ValueError):
            compiled.expand(**(expansion | {name: ["invalid IRI"]}))
    snapshot = _native.TargetData("", "nt", None)
    with pytest.raises(ValueError, match="Unknown shape"):
        compiled.focus_nodes("<urn:unknown>", snapshot, True)


@pytest.mark.parametrize(
    "call",
    [
        lambda: _native.infer("", "unknown", "rdfs"),
        lambda: _native.inoculate("", "unknown", ""),
        lambda: _native.query("", "unknown", "ASK {}"),
        lambda: _native.TargetData("", "unknown", None),
        lambda: _native.CompiledShapes("", "unknown", None, False, True, []),
    ],
)
def test_all_native_text_entry_points_reject_unknown_formats(call):
    with pytest.raises(NotImplementedError):
        call()


def test_native_parser_and_lazy_query_errors_propagate():
    with pytest.raises(ValueError):
        _native.parse_rdf("invalid RDF", "turtle", None)
    for query in [
        "ASK { SERVICE <https://example.org/unavailable> {?s ?p ?o} }",
        "SELECT ?s WHERE { SERVICE <https://example.org/unavailable> {?s ?p ?o} }",
    ]:
        with pytest.raises(RuntimeError):
            _native.query("", "nt", query)
