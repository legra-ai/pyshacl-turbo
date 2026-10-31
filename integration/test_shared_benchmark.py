"""The measured shared pipeline cannot silently use a converted backend."""

import importlib.util
from pathlib import Path

import pyshacl
import pyshacl_turbo
import pytest
from rdflib_turbo import Dataset


@pytest.mark.parametrize("mode", ["rdfs", "owlrl"])
def test_measured_pipeline_shares_the_dataset_and_materializes_only_the_report(monkeypatch, mode):
    path = Path(__file__).resolve().parents[1] / "benchmarks/companions.py"
    spec = importlib.util.spec_from_file_location("companions", path)
    bench = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bench)
    observed = []
    original = pyshacl_turbo.validate

    def capture(data, **options):
        assert isinstance(data, Dataset)
        observed.append(data.store.backend._native)
        return original(data, **options)

    def forbidden(*args, **kwargs):
        raise AssertionError("shared pipeline must never convert or run the reference engine")

    monkeypatch.setattr(pyshacl_turbo, "validate", capture)
    monkeypatch.setattr(pyshacl, "validate", forbidden)
    run, observe = bench.prepare(
        {"backend": "turbo_shared", "operation": f"pipeline_{mode}", "nodes": 10}
    )
    with monkeypatch.context() as patch:
        for name in ("to_rdflib", "from_rdflib", "serialize", "copy"):
            patch.setattr(Dataset, name, forbidden)
        value = run()
    assert observed == [value[0].store.backend._native]
    assert "report" in observe(value)
