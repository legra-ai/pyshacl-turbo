"""Public replay preserves exact cohorts, arm order and failed parity gates."""

import importlib.util
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "benchmarks" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_retained_repetition_alternates_arms_after_a_separate_warmup():
    driver = load("matched_graph_driver")
    assert driver.iteration_order(5) == [
        ("warmup", "reference"),
        ("warmup", "turbo"),
        ("sample1", "turbo"),
        ("sample1", "reference"),
        ("sample2", "reference"),
        ("sample2", "turbo"),
        ("sample3", "turbo"),
        ("sample3", "reference"),
        ("sample4", "reference"),
        ("sample4", "turbo"),
        ("sample5", "turbo"),
        ("sample5", "reference"),
    ]
    with pytest.raises(ValueError):
        driver.iteration_order(4)


def test_cohort_deduplication_requires_every_original_wheel_not_just_product_versions():
    authority = load("matched_graph_authority")
    wheels = {
        name: {"version": "1", "sha256": str(index) * 64}
        for index, name in enumerate(["rdflib-turbo", "owlrl-turbo", "pyshacl-turbo", "html5rdf"])
    }
    same = deepcopy(wheels)
    assert authority.cohort_key(wheels) == authority.cohort_key(same)
    same["html5rdf"]["sha256"] = "f" * 64
    assert authority.cohort_key(wheels) != authority.cohort_key(same)
    del same["html5rdf"]
    assert authority.cohort_key(wheels) != authority.cohort_key(same)


def test_failed_normal_policy_stops_before_a_timing_child(tmp_path):
    driver = load("matched_graph_driver")
    calls = []
    with pytest.raises(RuntimeError, match="correctness"):
        driver.sample_case(
            lambda *args: calls.append(args),
            {},
            {
                "normal": {"status": "different"},
                "width": 32,
                "profile": "literal-type",
            },
            tmp_path,
            5,
        )
    assert calls == []


def test_matrix_has_distinct_frozen_and_jointly_resolved_compatible_roles():
    driver = load("matched_graph_driver")
    import json

    matrix = json.loads((ROOT / "benchmarks/matched-graph-releases.json").read_text())
    environments = driver.validate_cohort(matrix)
    assert environments["baseline"]["requirements"] == {
        "rdflib-turbo": "==0.2.0a23",
        "owlrl-turbo": "==0.2.0a1",
        "pyshacl-turbo": "==0.7.1",
        "rdflib": "==7.6.0",
    }
    latest = environments["latest-compatible-released"]["requirements"]
    assert all(
        latest[name].startswith(">=") for name in ["rdflib-turbo", "owlrl-turbo", "pyshacl-turbo"]
    )
    malformed = deepcopy(matrix)
    malformed["environments"][1]["role"] = "reference"
    with pytest.raises(ValueError):
        driver.validate_cohort(malformed)


def test_old_twelve_cases_and_comparators_keep_their_inventory():
    releases = load("releases")
    jobs = releases.release_jobs([100, 1000])
    assert len(jobs) == 12
    assert sum(row["contract"] == "pipeline" for row in jobs) == 4
    assert {(row["fixture"], row["nodes"]) for row in jobs if row["contract"] == "inference"} == {
        (profile, width)
        for profile in ["literal-reflexivity", "literal-type"]
        for width in [32, 128, 512, 1000]
    }
