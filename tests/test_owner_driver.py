"""Native lifecycle orchestration preserves the sole published owner's authority."""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture(autouse=True)
def bytecode_disabled(monkeypatch):
    monkeypatch.setattr(sys, "dont_write_bytecode", True)


def helper():
    path = Path(__file__).resolve().parents[1] / "scripts/owner_driver.py"
    spec = importlib.util.spec_from_file_location("owner_driver", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_coverage_arguments_bind_original_provider_facade_and_owl_archives(tmp_path):
    authority = {
        "source_archive": str(tmp_path / "provider.tar.gz"),
        "source_sha256": "a" * 64,
        "collector_sha256": "b" * 64,
        "peers": {
            "owlrl": {
                "source": str(tmp_path / "owl"),
                "archive": str(tmp_path / "owl.tar.gz"),
                "sha256": "c" * 64,
                "wheel": str(tmp_path / "owl.whl"),
            },
            "yaml_test_dependency": {"authority": str(tmp_path / "yaml-inputs.json"), "record": {}},
        },
    }
    context = {
        "owner": tmp_path / "owner",
        "acceptance": tmp_path / "current-facade",
        "wheel": tmp_path / "original.whl",
        "output": tmp_path / "proof",
        "receipt": {
            "provider": authority,
            "execution_owlrl": dict(authority["peers"]["owlrl"]),
        },
    }
    authority["peers"]["owlrl"] = {"source": "immutable-build-peer"}
    args = helper().coverage_arguments(context)
    assert args.provider_source == context["owner"]
    assert args.facade_source == context["acceptance"]
    assert args.facade_wheel == context["wheel"]
    assert args.provider_revision is None
    assert args.source_archive == Path(authority["source_archive"])
    assert args.source_sha256 == "a" * 64
    assert args.collector_sha256 == "b" * 64
    assert args.owlrl_source == tmp_path / "owl"
    assert args.owlrl_archive == tmp_path / "owl.tar.gz"
    assert args.owlrl_sha256 == "c" * 64
    assert args.owlrl_wheel == tmp_path / "owl.whl"
    assert args.yaml_authority == tmp_path / "yaml-inputs.json"
    assert args.shacl_candidate_receipt is None and args.shacl_base_revision is None


def test_native_coverage_runs_owner_collector_before_build_gates_and_reattests(
    monkeypatch, tmp_path
):
    module = helper()
    events = []
    context = {
        "owner": tmp_path / "owner",
        "output": tmp_path / "proof",
        "environment": {"FROZEN": "1"},
    }
    validation = SimpleNamespace(
        prepare=lambda *args: context,
        verify_sources=lambda actual: events.append(("verify", actual)),
    )
    modules = {
        "provider_validation": validation,
        "provider_coverage": SimpleNamespace(measure=lambda args: events.append(("measure", args))),
        "owner_gates": SimpleNamespace(execute=lambda actual, gate: events.append((gate, actual))),
    }
    monkeypatch.setattr(module, "load", modules.__getitem__)
    monkeypatch.setattr(module, "coverage_arguments", lambda actual: "exact-original-archives")
    monkeypatch.setattr(module, "documentation", lambda actual: events.append(("docs", actual)))
    module.execute(tmp_path, tmp_path / "original.whl", tmp_path / "proof", "coverage")
    assert events == [
        ("measure", "exact-original-archives"),
        ("coverage", context),
        ("docs", context),
        ("verify", context),
    ]


def test_failed_registry_capability_never_starts_owner_gates(monkeypatch, tmp_path):
    module = helper()

    def unavailable(*args):
        raise ValueError("Declared published provider lacks SHACL capability")

    monkeypatch.setattr(module, "load", lambda name: SimpleNamespace(prepare=unavailable))
    with pytest.raises(ValueError, match="lacks SHACL capability"):
        module.execute(tmp_path, tmp_path / "original.whl", tmp_path / "proof", "coverage")


def test_regex_does_not_duplicate_collector_and_reattests(monkeypatch, tmp_path):
    module = helper()
    events = []
    context = {"owner": tmp_path}
    modules = {
        "provider_validation": SimpleNamespace(
            prepare=lambda *args: context, verify_sources=lambda actual: events.append("verified")
        ),
        "owner_gates": SimpleNamespace(execute=lambda actual, gate: events.append(gate)),
    }
    monkeypatch.setattr(module, "load", modules.__getitem__)
    module.execute(tmp_path, tmp_path / "original.whl", tmp_path / "proof", "regex")
    assert events == ["regex", "verified"]


def test_native_driver_rejects_bytecode_writes_before_resolving_authority(monkeypatch, tmp_path):
    module = helper()
    monkeypatch.setattr(module.sys, "dont_write_bytecode", False)
    monkeypatch.setattr(
        module, "load", lambda name: pytest.fail("Authority started before source-safety check")
    )
    with pytest.raises(ValueError, match="python -B"):
        module.execute(tmp_path, tmp_path / "original.whl", tmp_path / "proof", "coverage")
