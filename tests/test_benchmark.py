"""A speedup is valid only when both engines did the same validation work."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SH


def benchmark_module():
    path = Path(__file__).resolve().parents[1] / "benchmarks" / "matrix.py"
    spec = importlib.util.spec_from_file_location("benchmark_matrix", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_benchmark_method_describes_only_its_synthetic_fixture(tmp_path):
    module = benchmark_module()
    output = tmp_path / "performance.json"
    module.write_report(
        {
            "environment": {"date": "2026-10-14", "platform": "test", "python": "3.13"},
            "repeats": 1,
            "runs": [],
        },
        output,
    )
    method = next(
        line
        for line in output.with_suffix(".md").read_text().splitlines()
        if line.startswith("Warm median milliseconds.")
    )
    assert method.endswith("These are synthetic cases.")


def test_benchmark_rejects_missing_results_even_when_conformance_agrees():
    module = benchmark_module()
    case = module.make_case("core", 10, 1)
    expected = module.pyshacl.validate(case["data"], shacl_graph=case["shapes"])
    damaged = Graph()
    damaged += expected[1]
    damaged.remove((None, SH.result, None))
    with pytest.raises(AssertionError, match="report mismatch"):
        module.require_same_report(expected, (False, damaged, ""), "broken")


def test_benchmark_rejects_changed_message_or_value():
    module = benchmark_module()
    case = module.make_case("core", 10, 1)
    expected = module.pyshacl.validate(case["data"], shacl_graph=case["shapes"])
    damaged = Graph()
    damaged += expected[1]
    result = next(damaged.objects(None, SH.result))
    damaged.set((result, SH.resultMessage, Literal("changed")))
    with pytest.raises(AssertionError, match="report mismatch"):
        module.require_same_report(expected, (expected[0], damaged, ""), "broken")


def test_benchmark_preserves_duplicate_results_and_unconnected_triples():
    module = benchmark_module()
    case = module.make_case("core", 10, 1)
    expected = module.pyshacl.validate(case["data"], shacl_graph=case["shapes"])
    damaged = Graph()
    damaged += expected[1]
    root = damaged.value(None, RDF.type, SH.ValidationReport)
    result = next(damaged.objects(root, SH.result))
    duplicate = BNode()
    for _, p, o in list(damaged.triples((result, None, None))):
        damaged.add((duplicate, p, o))
    damaged.add((root, SH.result, duplicate))
    with pytest.raises(AssertionError, match="report mismatch"):
        module.require_same_report(expected, (expected[0], damaged, ""), "broken")
    damaged.remove((root, SH.result, duplicate))
    with pytest.raises(AssertionError, match="report mismatch"):
        module.require_same_report(expected, (expected[0], damaged, ""), "broken")


def test_inference_diagnostics_do_not_hide_generalized_triples():
    module = benchmark_module()
    reference, native = Graph(), Graph()
    resource = URIRef("urn:resource")
    reference.add((resource, RDF.type, RDFS.Resource))
    native += reference
    reference.add((Literal(1), RDF.type, RDFS.Resource))
    details = module.compare_inferred_graphs(reference, native)
    assert not details["graphs_isomorphic"]
    assert details["ordinary_rdf_graphs_isomorphic"]
    assert details["pyshacl_generalized_triples"] == 1
    assert details["turbo_generalized_triples"] == 0
    native.add((URIRef("urn:extra"), RDF.type, RDFS.Resource))
    assert not module.compare_inferred_graphs(reference, native)["ordinary_rdf_graphs_isomorphic"]


def test_benchmark_records_native_dependency_patches(tmp_path, monkeypatch):
    module = benchmark_module()
    output = tmp_path / "performance.json"
    monkeypatch.setattr(
        "sys.argv",
        ["matrix.py", "--quick", "--kinds", "core", "--repeats", "1", "--output", str(output)],
    )
    module.main()
    hashes = json.loads(output.read_text())["source_sha256"]
    for name in (
        "Cargo.lock",
        "Cargo.toml",
        "crates/engine/Cargo.toml",
        "vendor/oxrdf-0.3.4/src/literal.rs",
    ):
        assert hashes.get(name) == hashlib.sha256((module.ROOT / name).read_bytes()).hexdigest()
