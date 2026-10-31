"""The sampler must observe only after its absolute post-pipeline RSS read."""

import importlib.util
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
    expected = correctness.correctness(backend, 2, "literal-reflexivity", True)
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
