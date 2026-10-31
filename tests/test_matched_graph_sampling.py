"""The sampler must observe only after its absolute post-pipeline RSS read."""

import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest


def load(name):
    path = Path(__file__).resolve().parents[1] / "benchmarks" / (name + ".py")
    spec = importlib.util.spec_from_file_location(name + "_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("backend", ["reference", "turbo"])
def test_sampling_has_no_observer_between_operations_and_reads_rss_before_export(
    monkeypatch, backend
):
    correctness = load("matched_graph_fanout")
    expected = json.loads(
        json.dumps(correctness.correctness(backend, 2, "literal-reflexivity", True))
    )
    sampler = load("matched_graph_sampling")
    events = []
    original_facts = sampler.CONTRACT._suite

    def suite():
        value = original_facts()
        facts = value.FANOUT.facts

        def observe(graph):
            events.append("facts")
            return facts(graph)

        value.FANOUT.facts = observe
        return value

    monkeypatch.setattr(sampler.CONTRACT, "_suite", suite)
    monkeypatch.setattr(sampler, "peak_rss", lambda: events.append("rss") or 12345)
    result = sampler.sample(backend, 2, "literal-reflexivity", expected)
    assert result["gate"]["status"] == "equal"
    assert events[:3] == ["rss", "rss", "facts"]
    assert result["peak_rss_bytes"] == 12345
    assert set(result["stages"]) == {"construct_parse", "class_expand", "validate", "total"}
    assert all(value["wall_ns"] > 0 and value["cpu_ns"] > 0 for value in result["stages"].values())


def test_false_policy_cannot_enter_the_timing_pipeline():
    sampler = load("matched_graph_sampling")
    with pytest.raises(ValueError, match="normal=True"):
        sampler.sample(
            "reference", 2, "literal-reflexivity", {"before": {"normalize_literals": False}}
        )


def test_failed_sample_cannot_earn_speed_or_rss_ratios():
    sampler = load("matched_graph_sampling")
    sample = {
        "gate": {"status": "equal"},
        "stages": {"total": {"wall_ns": 20}},
        "peak_rss_bytes": 100,
    }
    failed = deepcopy(sample)
    failed["gate"]["status"] = "different"
    result = sampler.summarize([sample] * 5, [failed] * 5)
    assert result["speedup"] is None and result["rss_reduction"] is None
    assert result["status"] == "different"


@pytest.mark.parametrize("profile", ["literal-reflexivity", "literal-type"])
def test_actual_shared_graph_pipeline_never_exports_or_imports_data(monkeypatch, profile):
    """Non-timed tripwires; sampling children do not contain these spies."""
    from contextlib import contextmanager

    import rdflib
    from owlrl_turbo import DeductiveClosure, OWLRL_Semantics
    from pyshacl_turbo import validate
    from rdflib import Graph, URIRef
    from rdflib_turbo import Dataset, _native
    from rdflib_turbo import Graph as NativeGraph
    from rdflib_turbo._inference import GraphInference
    from rdflib_turbo._validation import GraphValidation
    from rdflib_turbo.store import Transaction

    sampler = load("matched_graph_sampling")
    suite = sampler.CONTRACT._suite()
    monkeypatch.setattr(rdflib, "NORMALIZE_LITERALS", True)
    source = NativeGraph(identifier=URIRef("urn:matched:graph")).parse(
        data=suite.FANOUT.fixture(2, profile), format="turtle"
    )
    shapes = Graph().parse(data=sampler.SHAPES, format="turtle")
    owner, handle = source.store, source.store.backend._native
    inference, validation = [], []
    infer = GraphInference._infer_bound_scope
    validate_shared = GraphValidation._validate_shared_shapes

    def forbidden(*args, **kwargs):
        raise AssertionError("DATA export/copy/import fallback reached")

    def infer_spy(self, *args, **kwargs):
        assert isinstance(self.store.backend, Transaction)
        inference.append(type(self.store.backend._native))
        return infer(self, *args, **kwargs)

    @contextmanager
    def validate_spy(self, program, settings, inplace):
        assert type(program) is _native.SharedShapes and inplace is True
        validation.append(isinstance(self.store.backend, Transaction))
        with validate_shared(self, program, settings, inplace) as result:
            yield result

    with monkeypatch.context() as tripwires:
        for name in ("triples", "__iter__", "serialize", "copy"):
            tripwires.setattr(NativeGraph, name, forbidden)
        tripwires.setattr(Dataset, "from_rdflib", forbidden)
        tripwires.setattr(GraphInference, "_infer_bound_scope", infer_spy)
        tripwires.setattr(GraphValidation, "_validate_shared_shapes", validate_spy)
        with pytest.raises(AssertionError, match="fallback"):
            source.serialize(format="turtle")
        assert DeductiveClosure(OWLRL_Semantics).expand(source, destination=source) is None
        conforms, report, text = validate(
            source, shacl_graph=shapes, inplace=True, inference="none"
        )
    assert inference == [_native.NativeTransaction]
    assert validation == [False, True]
    assert source.store is owner and owner.backend._native is handle
    assert conforms is True and len(report) == 2 and "Conforms: True" in text
    expected = sampler.CONTRACT.correctness("reference", 2, profile, True)
    assert suite.FANOUT.facts(source) == expected["complete_term_metadata"]
