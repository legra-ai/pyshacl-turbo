"""A new matched route must not rewrite the historical Dataset fanout gate."""

import importlib.util
from copy import deepcopy
from pathlib import Path

import pytest


def load():
    path = Path(__file__).resolve().parents[1] / "benchmarks/matched_graph_fanout.py"
    spec = importlib.util.spec_from_file_location("matched_graph_fanout_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("profile", ["literal-reflexivity", "literal-type"])
def test_small_public_graph_pipeline_complete_observation(profile):
    suite = load()
    observations = [
        suite.correctness(backend, 2, profile, True) for backend in ("reference", "turbo")
    ]
    assert observations[0]["operation"] == "matched_public_graph_pipeline"
    for observation in observations:
        assert observation["diagnostics"]["data_owner_preserved"]
        assert observation["effects"]["inference_returned_none"]
        assert observation["report"]["conforms"] is True
        assert observation["before"]["normalize_literals"] is True
    assert suite.differences(*observations) == []
    assert suite.comparison(*observations)["status"] == "equal"


def test_flag_only_difference_cannot_earn_performance_ratios():
    """Pinned 0.40.1/7.6.0 False-policy probe observed this difference.

    Inject the observation difference; no requirement that Original's module
    side effect persists in future interpreters or reference versions.
    """
    suite = load()
    observation = {"after": {"normalize_literals": False}, "error": None}
    other = deepcopy(observation)
    other["after"]["normalize_literals"] = True
    gate = suite.comparison(observation, other)
    assert gate == {
        "status": "different",
        "differences": ["after"],
        "speedup": None,
        "rss_reduction": None,
    }


def test_error_even_identical_cannot_earn_parity_or_ratios():
    suite = load()
    observation = {"error": {"phase": "validation", "type": "builtins.RuntimeError"}}
    assert suite.comparison(observation, observation) == {
        "status": "error",
        "differences": [],
        "speedup": None,
        "rss_reduction": None,
    }
