"""The original catalogue retains its exact recorded observation format."""

import hashlib
import importlib.util
from pathlib import Path

import pytest
from rdflib import Graph
from rdflib.compare import to_canonical_graph


def suite():
    path = Path(__file__).resolve().parents[1] / "benchmarks/companions.py"
    spec = importlib.util.spec_from_file_location("workload", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_legacy_worker_preserves_original_digest_bytes_without_leaking_its_encoder(monkeypatch):
    module = suite()
    graph = Graph().parse(data='_:focus <urn:p> "value".', format="turtle")
    lines = sorted(" ".join(term.n3() for term in triple) for triple in to_canonical_graph(graph))
    expected = {
        "triples": len(graph),
        "sha256": hashlib.sha256("\n".join(lines).encode()).hexdigest(),
    }
    monkeypatch.setattr(
        module, "measure_worker", lambda *args: {"observation": module.digest_graph(graph)}
    )
    legacy = module.worker({"observation_encoder": "rdflib-v1"}, 1, "memory")
    assert legacy["observation"] == expected
    current = module.worker({}, 1, "memory")
    assert current["observation"]["canonicalization"] == "unique-anchors-v1"


def test_worker_rejects_an_unknown_encoder_before_running_any_operation(monkeypatch):
    module = suite()

    def unexpected(job):
        raise AssertionError("Unknown encoders must fail before preparing data")

    monkeypatch.setattr(module, "prepare", unexpected)
    with pytest.raises(ValueError, match="observation encoder"):
        module.worker({"observation_encoder": "unknown"}, 1, "memory")


def test_failed_workers_restore_the_default_encoder(monkeypatch):
    module = suite()
    graph = Graph().parse(data='_:focus <urn:p> "value".', format="turtle")

    def failure(*args):
        assert "canonicalization" not in module.digest_graph(graph)
        raise RuntimeError("simulated worker failure")

    monkeypatch.setattr(module, "measure_worker", failure)
    with pytest.raises(RuntimeError, match="simulated worker failure"):
        module.worker({"observation_encoder": "rdflib-v1"}, 1, "memory")
    assert module.digest_graph(graph)["canonicalization"] == "unique-anchors-v1"
