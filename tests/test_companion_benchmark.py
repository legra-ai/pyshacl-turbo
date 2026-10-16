"""Reject misleading companion-project benchmark comparisons before timing claims."""

import importlib.util
import sys
from pathlib import Path

import pytest
from rdflib import BNode, Dataset, Graph, Literal, URIRef, Variable


def suite():
    path = Path(__file__).resolve().parents[1] / "benchmarks" / "companions.py"
    spec = importlib.util.spec_from_file_location("companion_benchmarks", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_comparison_never_turns_generalized_differences_into_full_parity():
    module = suite()
    graph = Graph().parse(data='<urn:a> <urn:p> "x" .', format="nt")
    native = module.graph_observation(graph)
    graph.add((Literal("x"), URIRef("urn:p"), URIRef("urn:a")))
    reference = module.graph_observation(graph)
    result = module.compare({"closure": reference}, {"closure": native}, 100, 10)
    assert result["status"] == "standard_rdf_equal"
    assert result["speedup"] is None
    graph.add((URIRef("urn:missing"), URIRef("urn:p"), Literal("x")))
    assert (
        module.compare({"closure": module.graph_observation(graph)}, {"closure": native}, 100, 10)[
            "status"
        ]
        == "different"
    )


def test_observation_preserves_scope_blank_node_sharing_and_literal_spellings():
    module = suite()
    source = Dataset().parse(
        data="""
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        <urn:g> { _:a <urn:p> _:b . }
        <urn:h> { _:b <urn:p> "01"^^xsd:integer . }
    """,
        format="trig",
    )
    same = Dataset().parse(data=source.serialize(format="nquads"), format="nquads")
    assert module.dataset_observation(source) == module.dataset_observation(same)
    changed = Dataset()
    for s, p, o, g in source.quads():
        changed.graph(URIRef("urn:other") if str(g) == "urn:g" else g).add((s, p, o))
    assert module.dataset_observation(source) != module.dataset_observation(changed)
    split = Dataset()
    for s, p, o, g in source.quads():
        split.graph(g).add((BNode("split") if str(g) == "urn:h" else s, p, o))
    assert module.dataset_observation(source) != module.dataset_observation(split)
    first, second = Graph(), Graph()
    first.add(
        (
            URIRef("urn:s"),
            URIRef("urn:p"),
            Literal("01", datatype=URIRef("urn:dt"), normalize=False),
        )
    )
    second.add(
        (URIRef("urn:s"), URIRef("urn:p"), Literal("1", datatype=URIRef("urn:dt"), normalize=False))
    )
    assert module.graph_observation(first) != module.graph_observation(second)


def test_select_observation_preserves_duplicate_rows_and_unbound_variables():
    module = suite()
    variables = [Variable("x"), Variable("unbound")]
    row = (URIRef("urn:a"), None)
    assert module.rows_observation(variables, [row, row]) != module.rows_observation(
        variables, [row]
    )
    assert module.rows_observation(variables, [row]) != module.rows_observation(
        variables[:1], [(row[0],)]
    )


def test_report_comparison_keeps_messages_and_disconnected_triples():
    module = suite()
    expected = {"report": {"conforms": False, "graph": "all-triples", "text": "message"}}
    actual = {"report": {"conforms": False, "graph": "missing-triples", "text": "message"}}
    assert module.compare(expected, actual, 100, 10)["speedup"] is None
    actual["report"]["graph"] = "all-triples"
    actual["report"]["text"] = "changed"
    assert module.compare(expected, actual, 100, 10)["status"] == "report_graph_equal"
    assert module.compare(expected, expected, 100, 10)["speedup"] == 10


def test_memory_units_are_explicit_and_platform_specific():
    module = suite()
    assert module.rss_bytes(20, "darwin") == 20
    assert module.rss_bytes(20, "linux") == 20480
    with pytest.raises(RuntimeError, match="Linux or macOS"):
        module.rss_bytes(20, "win32")


def test_catalogue_includes_conversions_and_complete_pipeline():
    module = suite()
    jobs = module.catalogue([10])
    names = {job["operation"] for job in jobs}
    assert {
        "parse_turtle",
        "parse_nquads",
        "select",
        "select_named",
        "ask",
        "construct",
        "serialize_nt",
        "serialize_nquads",
        "rdfs",
        "owlrl",
        "from_rdflib",
        "to_rdflib",
        "roundtrip",
        "validate",
        "pipeline_rdfs",
        "pipeline_owlrl",
    } <= names
    assert all(
        job["backends"] == ["turbo"]
        for job in jobs
        if job["operation"] in {"from_rdflib", "to_rdflib", "roundtrip"}
    )


@pytest.mark.skipif(sys.platform not in {"darwin", "linux"}, reason="POSIX memory worker")
def test_worker_retains_unstable_observations_and_disables_speedups(monkeypatch):
    module = suite()
    values = iter(
        [
            {"report": {"graph": "same", "text": "first"}},
            {"report": {"graph": "same", "text": "second"}},
        ]
    )
    monkeypatch.setattr(module, "prepare", lambda job: (lambda: next(values), lambda x: x))
    result = module.worker({"operation": "test", "backend": "turbo", "nodes": 1}, 1, "time")
    assert [value["report"]["text"] for value in result["observations"]] == ["first", "second"]
    assert not result["stable"]
    assert module.comparison_for_runs(result, result)["speedup"] is None


@pytest.mark.skipif(sys.platform not in {"darwin", "linux"}, reason="POSIX memory worker")
def test_worker_fails_fast_on_unstable_rdf(monkeypatch):
    module = suite()
    values = iter([{"query": "first"}, {"query": "changed"}])
    monkeypatch.setattr(module, "prepare", lambda job: (lambda: next(values), lambda x: x))
    with pytest.raises(RuntimeError, match="RDF observations are unstable"):
        module.worker({"operation": "test", "backend": "turbo", "nodes": 1}, 1, "time")


def test_named_fixture_formats_represent_the_same_dataset():
    module = suite()
    trig = Dataset().parse(data=module.fixture(100, named=True), format="trig")
    nquads = Dataset().parse(data=module.nquads_fixture(100), format="nquads")
    assert module.dataset_observation(trig) == module.dataset_observation(nquads)
