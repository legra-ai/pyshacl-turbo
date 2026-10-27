"""Scoped logical inference never silently changes the raw/pipeline contract."""

import copy

import pytest
from rdflib import Graph
from test_literal_fanout_benchmark import load


@pytest.fixture
def pair():
    suite = load("companions")
    run, observe = suite.prepare(
        {
            "operation": "owlrl",
            "backend": "reference",
            "nodes": 32,
            "fixture": "literal-reflexivity",
        }
    )
    left = observe(run())
    left["initial_term_metadata"] = suite.FANOUT.facts(
        Graph().parse(data=suite.fanout_fixture(32, "literal-reflexivity"), format="turtle")
    )
    right = copy.deepcopy(left)
    right["state"]["container"] = "rdflib_turbo.graph.StoreDataset"
    right["public_effects"].update(
        return_type="rdflib_turbo.graph.StoreDataset", returned_none=False, returned_input=True
    )

    def measured(value, ns):
        return {
            "observation": value,
            "observations": [copy.deepcopy(value), copy.deepcopy(value)],
            "memory_samples": [{"observation": copy.deepcopy(value)}],
            "samples_ns": [ns],
            "median_ns": ns,
            "stable": True,
        }

    return suite, measured(left, 100), measured(right, 50)


def logical(pair, left=None, right=None):
    suite, a, b = pair
    return suite.FANOUT.logical_inplace_owlrl(
        a if left is None else left,
        b if right is None else right,
        left_backend="reference",
        right_backend="turbo_shared",
    )


def test_scoped_ratio_is_additive_and_never_full_api_parity(pair):
    suite, left, right = pair
    before = copy.deepcopy((left, right))
    assert suite.comparison_for_runs(left, right) == {"status": "different", "speedup": None}
    assert logical(pair) == {"status": "logical_inplace_owlrl_equal", "speedup": 2.0}
    assert (left, right) == before


@pytest.mark.parametrize(
    "field,value",
    [("returned_none", True), ("returned_input", False), ("return_type", "builtins.NoneType")],
)
def test_native_route_must_really_return_same_source(pair, field, value):
    _, _, right = pair
    for value_observation in [
        right["observation"],
        *right["observations"],
        *[s["observation"] for s in right["memory_samples"]],
    ]:
        value_observation["public_effects"][field] = value
    with pytest.raises(RuntimeError):
        logical(pair)


def test_reference_none_and_container_are_validated_not_blindly_deleted(pair):
    _, left, _ = pair
    left["observation"]["public_effects"]["returned_none"] = False
    with pytest.raises(RuntimeError):
        logical(pair)


@pytest.mark.parametrize("where", ["time", "cold"])
def test_every_raw_warm_and_cold_observation_must_be_stable(pair, where):
    _, _, right = pair
    target = (
        right["observations"][1] if where == "time" else right["memory_samples"][0]["observation"]
    )
    target["namespaces_raw"] = list(reversed(target["namespaces_raw"]))
    assert logical(pair)["speedup"] is None


def test_namespace_order_is_still_required_even_when_binding_maps_match(pair):
    _, _, right = pair
    for obs in [
        right["observation"],
        *right["observations"],
        right["memory_samples"][0]["observation"],
    ]:
        obs["namespaces_raw"].reverse()
    assert logical(pair) == {"status": "logical_inplace_owlrl_different", "speedup": None}


@pytest.mark.parametrize("defect", ["duplicate", "missing_map", "wrong_map"])
def test_malformed_or_duplicate_namespace_authority_is_rejected(pair, defect):
    _, _, right = pair
    target = right["observation"]
    if defect == "duplicate":
        target["namespaces_raw"].append(target["namespaces_raw"][0])
    elif defect == "missing_map":
        del target["namespace_bindings"]
    else:
        target["namespace_bindings"]["forged"] = "urn:forged"
    with pytest.raises(RuntimeError):
        logical(pair)


@pytest.mark.parametrize(
    "field",
    [
        "initial_term_metadata",
        "complete_term_metadata",
        "public_effects",
        "decimal",
        "state",
        "input_sha256",
    ],
)
def test_missing_complete_observations_fail_not_downgrade(pair, field):
    _, _, right = pair
    del right["observation"][field]
    with pytest.raises(RuntimeError):
        logical(pair)


@pytest.mark.parametrize("defect", ["cache", "stdout", "warnings", "flags"])
def test_cache_effect_and_flag_differences_deny_scoped_ratio(pair, defect):
    _, _, right = pair
    for obs in [
        right["observation"],
        *right["observations"],
        right["memory_samples"][0]["observation"],
    ]:
        if defect == "cache":
            initial = obs["initial_term_metadata"][0]
            initial[2]["ill_typed"] = False
            for row in obs["complete_term_metadata"]:
                if row[:2] == initial[:2]:
                    row[2]["ill_typed"] = False
        elif defect == "stdout":
            obs["public_effects"]["stdout"] = "changed"
        elif defect == "warnings":
            obs["public_effects"]["warnings"] = [{"type": "UserWarning", "text": "changed"}]
        else:
            obs["decimal"]["flags_after"]["Inexact"] = True
    assert logical(pair)["speedup"] is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("container", "unapproved.Owner"),
        ("inplace", False),
        ("input_facts_preserved", False),
        ("logical_scope", "union"),
    ],
)
def test_route_and_logical_transition_state_cannot_be_forged(pair, field, value):
    _, _, right = pair
    right["observation"]["state"][field] = value
    with pytest.raises(RuntimeError):
        logical(pair)


@pytest.mark.parametrize(
    "defect", ["hash", "count", "missing_cold", "missing_warm", "missing_full"]
)
def test_input_inventory_and_complete_measurement_inventory_are_hard_gates(pair, defect):
    _, _, right = pair
    if defect == "hash":
        right["observation"]["input_sha256"] = "0" * 64
    elif defect == "count":
        right["observation"]["input_count"] = 10
    elif defect == "missing_cold":
        right["memory_samples"] = []
    elif defect == "missing_warm":
        right["observations"] = []
    else:
        del right["observation"]["closure"]["full"]
    with pytest.raises(RuntimeError):
        logical(pair)


def test_explicit_unstable_run_never_earns_a_scoped_ratio(pair):
    _, _, right = pair
    right["stable"] = False
    assert logical(pair) == {"status": "logical_inplace_owlrl_unstable", "speedup": None}


def test_release_consumer_and_markdown_keep_both_named_contracts(pair, tmp_path):
    suite, left, right = pair
    bench = load("releases")
    row = {
        "case": "literal-reflexivity",
        "nodes": 32,
        "contract": "inference",
        "environments": {"ref": left, "native": right},
        "comparisons": {"native": suite.comparison_for_runs(left, right)},
    }
    envs = [{"id": "ref", "backend": "reference"}, {"id": "native", "backend": "turbo_shared"}]
    row["availability"] = {
        env["id"]: {"schema": "literal-inplace-owlrl-v1", "status": "measured_validated"}
        for env in envs
    }
    bench.add_logical_inplace_comparisons(row, envs, "ref")
    assert row["comparisons"]["native"] == {"status": "different", "speedup": None}
    assert row["logical_inplace_owlrl"]["native"]["speedup"] == 2
    assert row["logical_inplace_between_versions"] == {}
    for value in row["environments"].values():
        value.update(
            min_ns=value["median_ns"], max_ns=value["median_ns"], median_peak_rss_bytes=1024
        )
    output = tmp_path / "report.json"
    bench.write_report(
        {
            "method": "test",
            "date": "test",
            "source_revision": "test",
            "source_tree_dirty": True,
            "runs": [row],
            "environments": {},
        },
        output,
    )
    text = output.with_suffix(".md").read_text()
    assert "Logical in-place OWL-RL status" in text
    assert "logical_inplace_owlrl_equal" in text
    assert "| different | — |" in text
    pipeline = {"contract": "pipeline"}
    bench.add_logical_inplace_comparisons(pipeline, envs, "ref")
    assert pipeline == {"contract": "pipeline"}


def test_future_native_contract_requires_complete_valid_worker_before_transition(pair, monkeypatch):
    from test_fanout_availability import identity

    _, _, right = pair
    bench = load("releases")
    env = {"id": "future-candidate", "backend": "turbo_shared"}
    job = {
        "contract": "inference",
        "fixture": "literal-reflexivity",
        "operation": "owlrl",
        "nodes": 32,
    }
    row = {"contract": "inference", "environments": {}}
    monkeypatch.setattr(bench, "measure", lambda *_: copy.deepcopy(right))
    bench.measure_environment(
        row, env, identity(version="99.1"), "actual-contract-fixture", job, 1, 1, 5
    )
    assert row["availability"][env["id"]]["status"] == "measured_validated"
    for defect in ("return", "unstable", "missing"):
        bad = copy.deepcopy(right)
        if defect == "return":
            bad["observation"]["public_effects"]["returned_input"] = False
        elif defect == "unstable":
            bad["stable"] = False
        else:
            del bad["observation"]["complete_term_metadata"]
        monkeypatch.setattr(bench, "measure", lambda *_, value=bad: value)
        broken = {"contract": "inference", "environments": {}}
        with pytest.raises(RuntimeError):
            bench.measure_environment(broken, env, identity(), "fixture", job, 1, 1, 5)
        assert broken["availability"][env["id"]]["status"] == "contract_pending"
        assert env["id"] in broken["environments"]  # Retain actual failing observation.
