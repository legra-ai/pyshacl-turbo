"""The measurement must detect differences, including broken reference runs."""

import importlib.util
import sys
from pathlib import Path

import pytest
from rdflib import BNode, Dataset, Graph, Literal, URIRef

SPEC = importlib.util.spec_from_file_location(
    "compare_contract", Path(__file__).resolve().parents[1] / "scripts/compare_contract.py"
)
measurement = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = measurement
SPEC.loader.exec_module(measurement)


def test_graph_snapshot_preserves_structure_but_not_generated_blank_node_labels():
    first, second = Graph(), Graph()
    for graph, node in ((first, BNode("first")), (second, BNode("second"))):
        graph.add((node, URIRef("urn:p"), Literal("value")))
    assert measurement.rdf_snapshot(first) == measurement.rdf_snapshot(second)
    second.add((BNode("extra"), URIRef("urn:p"), Literal("value")))
    assert measurement.rdf_snapshot(first) != measurement.rdf_snapshot(second)


def test_graph_snapshot_distinguishes_graph_names_and_shared_blank_nodes():
    first, second = Dataset(), Dataset()
    triple = BNode("shared"), URIRef("urn:p"), Literal("value")
    first.default_graph.add(triple)
    second.graph(URIRef("urn:named")).add(triple)
    assert measurement.rdf_snapshot(first) != measurement.rdf_snapshot(second)
    first.graph(URIRef("urn:named")).add(triple)
    second.default_graph.add((BNode("different"), triple[1], triple[2]))
    assert measurement.rdf_snapshot(first) != measurement.rdf_snapshot(second)


def test_graph_name_cannot_collide_with_default_graph_marker():
    first, second = Dataset(), Dataset()
    triple = URIRef("urn:s"), URIRef("urn:p"), Literal("value")
    first.default_graph.add(triple)
    second.graph(URIRef("urn:contract:default-graph")).add(triple)
    assert measurement.rdf_snapshot(first) != measurement.rdf_snapshot(second)


def test_missing_field_is_different_even_if_expected_value_is_none():
    result = measurement.compare(
        {"state": "ok", "observation": {"mutation": None}},
        {"state": "ok", "observation": {}},
    )
    assert result["status"] == "different"


@pytest.mark.parametrize("field", ["report", "mutation", "text", "error", "warnings", "type"])
def test_comparison_rejects_each_changed_contract_field(field):
    reference = {"state": "ok", "observation": {field: "expected"}, "samples_ns": [100]}
    turbo = {"state": "ok", "observation": {field: "changed"}, "samples_ns": [1]}
    result = measurement.compare(reference, turbo)
    assert result["status"] == "different"
    assert result["different_fields"] == [field]
    assert "speedup" not in result


@pytest.mark.parametrize("state", ["error", "timeout", "crash"])
def test_reference_failure_cannot_count_as_compatibility_or_speedup(state):
    result = measurement.compare({"state": state}, {"state": "ok", "observation": {}})
    assert result["status"] == f"reference_{state}"
    assert "speedup" not in result


def test_only_matching_successful_calls_receive_speedups():
    result = measurement.compare(
        {"state": "ok", "observation": {"conforms": True}, "samples_ns": [20, 10, 30]},
        {"state": "ok", "observation": {"conforms": True}, "samples_ns": [2, 1, 3]},
    )
    assert result["status"] == "equal"
    assert result["speedup"] == 10


def test_worker_timeout_is_bounded_and_recorded():
    result = measurement.run_process([sys.executable, "-c", "while True: pass"], timeout=0.1)
    assert result["state"] == "timeout"


def test_worker_crash_and_invalid_protocol_are_not_passes():
    result = measurement.run_process([sys.executable, "-c", "raise SystemExit(7)"], timeout=5)
    assert result["state"] == "crash" and result["exit_code"] == 7
    result = measurement.run_process([sys.executable, "-c", "print('bad json')"], timeout=5)
    assert result["state"] == "error"


def test_gate_rejects_lost_cases_duplicates_and_regressions():
    baseline = {
        "a": {"status": "equal"},
        "b": {"status": "different", "different_fields": ["text"]},
    }
    measurement.check_baseline(
        [{"id": "a", "status": "equal"}, {"id": "b", "status": "equal"}], baseline
    )
    for rows in (
        [{"id": "a", "status": "equal"}],
        [{"id": "a", "status": "equal"}, {"id": "a", "status": "equal"}],
        [{"id": "a", "status": "different"}, {"id": "b", "status": "different"}],
    ):
        with pytest.raises(RuntimeError):
            measurement.check_baseline(rows, baseline)


def test_gate_rejects_new_differences_inside_an_already_different_case():
    baseline = {"a": {"status": "different", "different_fields": ["text"]}}
    measurement.check_baseline(
        [{"id": "a", "status": "different", "different_fields": ["text"]}], baseline
    )
    with pytest.raises(RuntimeError):
        measurement.check_baseline(
            [{"id": "a", "status": "different", "different_fields": ["text", "report"]}], baseline
        )


def test_gate_rejects_turbo_errors_when_reference_already_fails():
    baseline = {"a": {"status": "reference_error", "turbo_state": "ok"}}
    measurement.check_baseline(
        [{"id": "a", "status": "reference_error", "turbo_state": "ok"}], baseline
    )
    with pytest.raises(RuntimeError):
        measurement.check_baseline(
            [{"id": "a", "status": "reference_error", "turbo_state": "error"}], baseline
        )


def test_audit_refuses_an_accidentally_redirected_reference(monkeypatch):
    import pyshacl
    import pyshacl_turbo

    monkeypatch.setattr(pyshacl, "validate", pyshacl_turbo.validate)
    with pytest.raises(RuntimeError, match="redirect"):
        measurement.worker("pyshacl", {"kind": "export", "name": "validate"}, 1)
