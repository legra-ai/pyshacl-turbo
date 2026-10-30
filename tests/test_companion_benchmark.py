"""Reject misleading companion-project benchmark comparisons before timing claims."""

import importlib.util
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest
from rdflib import BNode, Dataset, Graph, Literal, URIRef, Variable


def suite():
    path = Path(__file__).resolve().parents[1] / "benchmarks" / "companions.py"
    spec = importlib.util.spec_from_file_location("companion_benchmarks", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def locked_environment(tmp_path, monkeypatch):
    module = suite()
    for relative in (
        "benchmarks/companions.py",
        "benchmarks/inference_fanout.py",
        "benchmarks/pyproject.toml",
        "benchmarks/uv.lock",
        "tests/upstream_support/process_launch.py",
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((module.ROOT / relative).read_bytes())
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "__file__", str(tmp_path / "benchmarks/companions.py"))
    lock = tomllib.loads((tmp_path / "benchmarks/uv.lock").read_text())
    versions = {
        package["name"]: package["version"]
        for package in lock["package"]
        if "registry" in package["source"]
    }
    monkeypatch.setattr(
        module,
        "distribution",
        lambda name: SimpleNamespace(version=versions[name], read_text=lambda _: None, files=[]),
    )
    return module, versions


@pytest.mark.parametrize("stale_export", [False, True])
def test_environment_reads_uv_lock_without_an_exported_lock(locked_environment, stale_export):
    module, versions = locked_environment
    if stale_export:
        (module.ROOT / "benchmarks/companions-requirements.lock").write_text("wcwidth==0.0.0\n")
    environment = module.environment()
    assert environment["packages"].keys() == versions.keys()
    assert environment["packages"]["wcwidth"]["version"] == versions["wcwidth"]
    assert "benchmarks/companions-requirements.lock" not in environment["source_sha256"]


@pytest.mark.parametrize("source", ['git = "https://example.com/source"', 'path = "../source"'])
def test_environment_rejects_nonregistry_uv_sources(locked_environment, source):
    module, _ = locked_environment
    (module.ROOT / "benchmarks/uv.lock").write_text(
        '[[package]]\nname = "wcwidth"\nversion = "0.9.3"\nsource = {' + source + "}\n"
    )
    with pytest.raises(RuntimeError, match="PyPI"):
        module.environment()


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


@pytest.mark.parametrize("backend", ["turbo", "turbo_shared"])
def test_pipeline_observes_complete_inference_destination(monkeypatch, backend):
    """A native Dataset's named inference destination is part of its closure."""
    from owlrl import DeductiveClosure, RDFS_Semantics

    module = suite()
    text = "<urn:s> a <urn:C> . <urn:C> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <urn:D> ."
    original = Graph().parse(data=text, format="turtle")
    premises = set(original)
    DeductiveClosure(RDFS_Semantics).expand(original)
    assert len(premises) == 2
    assert len(original) == 12
    dataset = Dataset()
    for triple in premises:
        dataset.default_graph.add(triple)
    for triple in set(original) - premises:
        dataset.graph(URIRef("urn:owlrl-turbo:inference")).add(triple)
    # Physical duplicate contexts must not multiply the logical closure.
    dataset.graph(URIRef("urn:duplicate")).add(next(iter(premises)))
    physical = module.dataset_observation(dataset)

    class NativeDataset:
        def parse(self, **kwargs):
            return self

        def to_rdflib(self):
            return dataset

    native = NativeDataset()
    validated = []

    def expand(source, **kwargs):
        assert kwargs == {"inference": "rdfs", "inplace": True}
        return native

    def validate(source, **kwargs):
        validated.append(source)
        return True, Graph(), "Validation Report\nConforms: True\n"

    monkeypatch.setattr(module, "fixture", lambda *args, **kwargs: text)
    monkeypatch.setitem(sys.modules, "rdflib_turbo", SimpleNamespace(Dataset=NativeDataset))
    monkeypatch.setitem(sys.modules, "owlrl_turbo", SimpleNamespace(expand=expand))
    monkeypatch.setitem(sys.modules, "pyshacl_turbo", SimpleNamespace(validate=validate))
    run, observe = module.prepare({"operation": "pipeline_rdfs", "backend": backend, "nodes": 1})
    result = run()
    if backend == "turbo_shared":
        assert validated == [native]  # No conversion enters the shared timed operation.
    else:
        assert module.graph_observation(validated[0]) == module.graph_observation(original)
    assert observe(result)["closure"] == module.graph_observation(original)
    assert module.dataset_observation(dataset) == physical
    assert len(dataset.default_graph) == 2
    assert len(dataset.graph(URIRef("urn:owlrl-turbo:inference"))) == 10
    assert physical["quads"] == 13


def test_logical_closure_keeps_generalized_facts_and_deduplicates_contexts():
    module = suite()
    dataset = Dataset()
    ordinary = (URIRef("urn:s"), URIRef("urn:p"), Literal("value"))
    generalized = (Literal("value"), URIRef("urn:p"), URIRef("urn:s"))
    dataset.default_graph.add(ordinary)
    named = dataset.graph(URIRef("urn:inference"))
    named.add(ordinary)
    named.add(generalized)
    physical = module.dataset_observation(dataset)
    result = module.graph_observation(module.logical_graph(dataset))
    assert result["ordinary"]["triples"] == 1
    assert result["full"]["triples"] == 2
    assert result["generalized_triples"] == 1
    assert module.dataset_observation(dataset) == physical
    assert physical["quads"] == 3
