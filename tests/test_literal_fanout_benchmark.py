"""Keep literal fanout inside the shared public-operation benchmark workers."""

import hashlib
import importlib.util
from pathlib import Path

import pytest
from rdflib import Literal, URIRef


def load(name):
    path = Path(__file__).resolve().parents[1] / "benchmarks" / (name + ".py")
    spec = importlib.util.spec_from_file_location("fanout_test_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GOLDENS = {
    ("literal-reflexivity", 32): "8278292677c21bd2326e64c01b7d9d9fd117f217682ca9ee80fb8e958eab5c84",
    (
        "literal-reflexivity",
        128,
    ): "7dc437bac16b0c37f98e3f98b382d6ae41a8cd33f8328e803e8747462220dbb0",
    (
        "literal-reflexivity",
        512,
    ): "3447918d15997be097d7573699e336897793ace1a8e0db8f91af3f047564df7f",
    (
        "literal-reflexivity",
        1000,
    ): "de05adb488654f4ac1caaea5642034130b9ebbc8b4a3389f492fa85db44af1c3",
    ("literal-type", 32): "e38463cd4077cf0ba6b62bacd9395f1d8076978022ec6d7a71352d051ddbff23",
    ("literal-type", 128): "488d8e1ed308297a269a2b5c12efd0736289af5b7320892ec6e3a31b0e0d2e91",
    ("literal-type", 512): "a2535721ca5080b42577e926789c062653cf7cff351364cea4f8b287fac13f28",
    ("literal-type", 1000): "e5f1315ddbef814fd1379a9de068a291bcd8da058c66893824ca5018f8439b70",
}


@pytest.mark.parametrize("profile,width", GOLDENS)
def test_fanout_inputs_keep_the_sealed_diagnostic_bytes(profile, width):
    suite = load("companions")
    text = suite.fanout_fixture(width, profile)
    assert hashlib.sha256(text.encode()).hexdigest() == GOLDENS[profile, width]


def test_reference_worker_executes_literal_fanout_not_employee_fixture():
    suite = load("companions")
    run, observe = suite.prepare(
        {
            "operation": "owlrl",
            "backend": "reference",
            "nodes": 32,
            "fixture": "literal-reflexivity",
        }
    )
    value = run()
    assert (URIRef("urn:membership:s0"), URIRef("urn:membership:p"), Literal("value-0")) in value
    result = observe(value)
    assert result["input_sha256"] == GOLDENS["literal-reflexivity", 32]
    assert result["operation"] == "owlrl_inplace"
    assert result["state"]["input_facts_preserved"]


def test_release_inventory_keeps_pipeline_and_adds_only_closed_fanout_profiles():
    bench = load("releases")
    jobs = bench.release_jobs([100])
    assert [(j["operation"], j["nodes"]) for j in jobs if j["contract"] == "pipeline"] == [
        ("pipeline_rdfs", 100),
        ("pipeline_owlrl", 100),
    ]
    fanout = [j for j in jobs if j["contract"] == "inference"]
    assert {(j["fixture"], j["nodes"]) for j in fanout} == set(GOLDENS)
    assert all(j["operation"] == "owlrl" for j in fanout)


@pytest.mark.parametrize(
    "profile,width",
    [("unknown", 32), ("literal-type", 0), ("literal-type", 1001), ("literal-type", True)],
)
def test_closed_fanout_rejects_unknown_or_unbounded_recipes(profile, width):
    with pytest.raises(ValueError):
        load("companions").fanout_fixture(width, profile)


def test_literal_metadata_does_not_launder_assessment_or_float_bits():
    from decimal import Decimal

    from rdflib.namespace import XSD

    helper = load("companions").FANOUT
    constructor, assessed = Literal(1), Literal("1", datatype=XSD.integer)
    assert constructor == assessed
    assert helper.term(constructor) != helper.term(assessed)
    assert helper.cache(-0.0) != helper.cache(0.0)
    assert helper.cache(Decimal("1.20"))["value"] == [0, [1, 2, 0], -2]
    with pytest.raises(RuntimeError, match="Unsupported cache"):
        helper.cache(object())


def test_namespace_binding_equality_does_not_hide_raw_order_difference():
    suite = load("companions")
    left = {
        "namespaces_raw": [("a", "urn:a"), ("b", "urn:b")],
        "namespace_bindings": {"a": "urn:a", "b": "urn:b"},
    }
    right = {**left, "namespaces_raw": list(reversed(left["namespaces_raw"]))}
    assert suite.compare(left, right, 100, 1) == {"status": "different", "speedup": None}


def test_inplace_setup_and_observation_remain_outside_existing_worker_timer(monkeypatch):
    import owlrl

    suite = load("companions")
    events = []

    class Closure:
        def __init__(self, _):
            pass

        def expand(self, source):
            events.append("expand")
            source.add((URIRef("urn:derived"), URIRef("urn:p"), Literal("derived")))

    monkeypatch.setattr(owlrl, "DeductiveClosure", Closure)
    prepare = suite.prepare

    def wrapped(job):
        events.append("setup")
        run, observe = prepare(job)
        events.append("ready")

        def observation(value):
            events.append("observe")
            return observe(value)

        return run, observation

    ticks = iter([10, 20, 30, 40])

    def clock():
        events.append("clock")
        return next(ticks)

    monkeypatch.setattr(suite, "prepare", wrapped)
    monkeypatch.setattr(suite.time, "perf_counter_ns", clock)
    result = suite.worker(
        {"operation": "owlrl", "backend": "reference", "nodes": 32, "fixture": "literal-type"},
        1,
        "time",
    )
    assert events == ["setup", "ready", "clock", "expand", "clock", "observe"] * 2
    assert result["samples_ns"] == [10]
    assert len(result["observations"]) == 2
    assert result["observation"]["public_effects"]["returned_none"]
    assert not result["observation"]["public_effects"]["returned_input"]


def test_inplace_changes_to_existing_literal_cache_fail_observation(monkeypatch):
    import owlrl

    suite = load("companions")

    class Closure:
        def __init__(self, _):
            pass

        def expand(self, source):
            source.remove((URIRef("urn:membership:s0"), None, None))

    monkeypatch.setattr(owlrl, "DeductiveClosure", Closure)
    run, observe = suite.prepare(
        {"operation": "owlrl", "backend": "reference", "nodes": 32, "fixture": "literal-type"}
    )
    with pytest.raises(RuntimeError, match="input fact or its literal cache"):
        observe(run())


def test_cold_worker_runs_once_and_captures_peak_before_observation(monkeypatch):
    import resource
    from types import SimpleNamespace

    suite = load("companions")
    events = []

    def prepare(_):
        events.append("setup")

        def run():
            events.append("expand")
            return "result"

        def observe(value):
            assert value == "result"
            events.append("observe")
            return {"complete": True}

        return run, observe

    values = iter([10, 20])

    def usage(_):
        events.append("rss")
        return SimpleNamespace(ru_maxrss=next(values))

    monkeypatch.setattr(suite, "prepare", prepare)
    monkeypatch.setattr(resource, "getrusage", usage)
    result = suite.worker({"observation_encoder": "unique-anchors-v1"}, 7, "memory")
    assert events == ["setup", "rss", "expand", "rss", "observe"]
    assert result["samples_ns"] == []
    assert len(result["observations"]) == 1
    assert result["peak_rss_bytes"] == suite.rss_bytes(20, suite.sys.platform)
    assert result["setup_peak_rss_bytes"] == suite.rss_bytes(10, suite.sys.platform)


def test_inference_contract_never_waives_pipeline_report_or_missing_observations():
    bench = load("releases")
    observation = {
        "closure": {"ordinary": "same"},
        **{
            key: {}
            for key in [
                "complete_term_metadata",
                "namespaces_raw",
                "namespace_bindings",
                "public_effects",
                "decimal",
                "state",
            ]
        },
    }
    measured = {"observation": observation}
    bench.require_standard_parity(measured, measured, contract="inference")
    with pytest.raises(RuntimeError, match="mandatory pipeline report"):
        bench.require_standard_parity(measured, measured)
    incomplete = {"observation": {"closure": {"ordinary": "same"}}}
    with pytest.raises(RuntimeError, match="Missing complete"):
        bench.require_standard_parity(incomplete, measured, contract="inference")
    with pytest.raises(ValueError, match="Unknown"):
        bench.require_standard_parity(measured, measured, contract="unknown")
