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


def test_complete_artifact_manifest_does_not_reference_unpublished_virtualenvs(tmp_path):
    driver = load("matched_graph_driver")
    paths = [
        "proofs/case.json.gz",
        "locks/baseline/uv.lock",
        "originals/provider.whl",
        "originals/provider.tar.gz",
        "released-baseline/.venv/data.json",
    ]
    for name in paths:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"preserve this file")
    assert set(driver.proof_hashes(tmp_path)) == set(paths[:-1])


def test_even_matching_public_errors_stop_before_timing(tmp_path):
    driver = load("matched_graph_driver")
    calls = []

    def invoke(project, job, proof):
        calls.append(job["kind"])
        driver.WORKER.write_proof(
            proof, {"observation": {"error": {"type": "builtins.ValueError"}}}
        )

    with pytest.raises(RuntimeError, match="correctness.*error"):
        driver.check_case(
            invoke, {"reference": tmp_path, "turbo": tmp_path}, 32, "literal-type", tmp_path
        )
    assert calls == ["correctness", "correctness"]


def test_lock_replay_uses_locked_sync_without_resolving_or_rewriting_input(tmp_path, monkeypatch):
    authority = load("matched_graph_authority")
    lock = tmp_path / "supplied.lock"
    lock.write_text("immutable original lock")
    commands = []

    def command(argv):
        commands.append(list(map(str, argv)))
        if argv[1] == "init":
            project = Path(argv[-1])
            project.mkdir()
            (project / "pyproject.toml").write_text(
                '[project]\nname = "baseline"\nversion = "0.1.0"\nrequires-python = ">=3.13"\ndependencies = []\n'
            )
        return ""

    monkeypatch.setattr(authority.RELEASES, "command", command)
    monkeypatch.setattr(authority, "identity", lambda *args: {})
    project, _ = authority.setup(
        {"id": "baseline", "requirements": {"rdflib": "==7.6.0"}},
        tmp_path,
        "3.13.16",
        Path("driver.py"),
        lock,
    )
    assert (project / "uv.lock").read_bytes() == lock.read_bytes()
    assert not any(argv[1] == "add" for argv in commands)
    assert commands[-1][1] == "sync" and "--locked" in commands[-1] and "--no-build" in commands[-1]
