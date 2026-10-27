"""Closed observer contracts admit artifacts, never arbitrary version ranges."""

import copy

import pytest
from test_literal_fanout_benchmark import load


def identity(*, native=True, historical=False, version="99.1"):
    names = (
        ("rdflib-turbo", "owlrl-turbo", "pyshacl-turbo")
        if native
        else ("rdflib", "owlrl", "pyshacl")
    )
    versions = ("0.1.0a2", "0.1.0a2", "0.2.4") if historical else (version,) * 3
    return {
        "packages": {
            name: {"version": v, "payload_sha256": {"public.py": "a" * 64}}
            for name, v in zip(names, versions, strict=True)
        },
        "uv_lock_sha256": "b" * 64,
        "fanout_observer": {
            "schema": "literal-inplace-owlrl-v1",
            "route": "native" if native else "reference",
            "namespace_attribute_absent": historical,
            "apis": {"parse": True, "namespaces": not historical, "export": True, "invoke": True},
        },
    }


def test_known_a2_exclusion_is_before_worker_and_requires_actual_absence():
    bench = load("releases")
    proof = identity(historical=True)
    decision = bench.availability.prepare(proof, "turbo")
    assert decision["status"] == "not_measured_observer_unavailable"
    assert "Dataset.namespaces" in decision["reason"]
    assert "measurement" not in decision and "speedup" not in decision
    changed = copy.deepcopy(proof)
    changed["fanout_observer"]["namespace_attribute_absent"] = False
    with pytest.raises(RuntimeError):
        bench.availability.prepare(changed, "turbo")
    proof["fanout_observer"]["apis"]["namespaces"] = True
    with pytest.raises(RuntimeError):
        bench.availability.prepare(proof, "turbo")


def test_new_versions_use_explicit_contract_not_semver_allowlist():
    bench = load("releases")
    for backend in ("turbo", "turbo_shared", "reference"):
        proof = identity(native=backend != "reference")
        decision = bench.availability.prepare(proof, backend)
        assert decision["status"] == "contract_pending"
        assert decision["versions"] and decision["uv_lock_sha256"] == "b" * 64
        assert decision["payload_sha256"]


@pytest.mark.parametrize("defect", ["backend", "schema", "route", "api", "lock", "payload"])
def test_unknown_or_incomplete_contract_cannot_be_admitted(defect):
    bench = load("releases")
    proof, backend = identity(), "turbo_shared"
    if defect == "backend":
        backend = "unknown"
    elif defect == "schema":
        proof["fanout_observer"]["schema"] = "future"
    elif defect == "route":
        proof["fanout_observer"]["route"] = "reference"
    elif defect == "api":
        proof["fanout_observer"]["apis"]["export"] = False
    elif defect == "lock":
        del proof["uv_lock_sha256"]
    else:
        proof["packages"]["rdflib-turbo"]["payload_sha256"] = {}
    with pytest.raises(RuntimeError):
        bench.availability.prepare(proof, backend)


def test_only_explicit_validated_measurements_are_selected():
    bench = load("releases")
    envs = [{"id": "ref", "backend": "reference"}, {"id": "old", "backend": "turbo"}]
    row = {
        "contract": "inference",
        "environments": {"ref": {"actual": True}},
        "availability": {
            "ref": {"schema": "literal-inplace-owlrl-v1", "status": "measured_validated"},
            "old": bench.availability.prepare(identity(historical=True), "turbo"),
        },
    }
    assert bench.availability.measured(row, envs) == envs[:1]
    for defect in ("missing", "unknown", "pending", "fake_observation"):
        broken = copy.deepcopy(row)
        if defect == "missing":
            del broken["availability"]["old"]
        elif defect == "fake_observation":
            broken["environments"]["old"] = {}
        else:
            broken["availability"]["old"]["status"] = (
                "contract_pending" if defect == "pending" else "unknown"
            )
        with pytest.raises(RuntimeError):
            bench.availability.measured(broken, envs)
    pipeline = {"contract": "pipeline"}
    assert bench.availability.measured(pipeline, envs) == envs
    jobs = bench.release_jobs([32])
    assert [j["case"] for j in jobs if j["contract"] == "pipeline"] == [
        "pipeline_rdfs",
        "pipeline_owlrl",
    ]


def test_known_exclusion_never_invokes_serial_worker_and_is_visible(monkeypatch, tmp_path):
    bench = load("releases")
    env = {"id": "old", "backend": "turbo"}
    job = {
        "case": "literal-type",
        "contract": "inference",
        "fixture": "literal-type",
        "nodes": 32,
        "operation": "owlrl",
    }
    row = {**job, "environments": {}, "comparisons": {}}

    def forbidden(*_, **__):
        pytest.fail("Known excluded observer was invoked")

    monkeypatch.setattr(bench, "measure", forbidden)
    bench.measure_environment(row, env, identity(historical=True), "unused", job, 1, 1, 5)
    assert not row["environments"] and not row["comparisons"]
    output = tmp_path / "result.json"
    bench.write_report(
        {
            "method": "test",
            "date": "test",
            "source_revision": "test",
            "source_tree_dirty": False,
            "runs": [row],
            "environments": {},
        },
        output,
    )
    assert "not_measured_observer_unavailable" in output.read_text()
    assert "Dataset.namespaces" in output.with_suffix(".md").read_text()
    assert "not measured | —" in output.with_suffix(".md").read_text()
