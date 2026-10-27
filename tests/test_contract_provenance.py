"""Compatibility provenance identifies pure source and the actual shared DSO."""

import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


def helper():
    spec = importlib.util.spec_from_file_location(
        "contract_provenance", ROOT / "scripts/compare_contract.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_actual_pure_checkout_fingerprint_does_not_require_a_removed_native_build():
    assert len(helper().source_fingerprint()) == 64


def test_pure_fingerprint_binds_assets_and_required_manifests(tmp_path, monkeypatch):
    module = helper()
    (tmp_path / "python/assets").mkdir(parents=True)
    asset = tmp_path / "python/assets/shapes.ttl"
    asset.write_text("original")
    (tmp_path / "pyproject.toml").write_text("pure build")
    (tmp_path / "uv.lock").write_text("locked inputs")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    original = module.source_fingerprint()
    asset.write_text("changed")
    assert module.source_fingerprint() != original
    (tmp_path / "uv.lock").unlink()
    with pytest.raises(FileNotFoundError):
        module.source_fingerprint()


def installed_pair(tmp_path, monkeypatch):
    module = helper()
    native = tmp_path / "rdflib_turbo/_native.so"
    native.parent.mkdir()
    native.write_bytes(b"native wheel binary")
    facade = tmp_path / "pyshacl_turbo/_native.py"
    facade.parent.mkdir()
    facade.write_bytes(b"pure facade")
    bindings = SimpleNamespace(
        CompiledShapes=object(), TargetData=object(), SHACL_ENGINE_FINGERPRINT="a" * 64
    )
    provider = SimpleNamespace(__file__=str(native), shacl=bindings)
    pure = SimpleNamespace(__file__=str(facade), **vars(bindings))
    modules = {"rdflib_turbo._native": provider, "pyshacl_turbo._native": pure}
    monkeypatch.setattr(module.importlib, "import_module", lambda name: modules[name])
    monkeypatch.setattr(module, "version", lambda name: "fixture")
    return module, provider, pure, native


def test_native_digest_is_the_provider_dso_not_the_python_facade(tmp_path, monkeypatch):
    module, _, _, native = installed_pair(tmp_path, monkeypatch)
    actual = module.runtime_provenance()
    assert actual["native_binary_sha256"] == hashlib.sha256(native.read_bytes()).hexdigest()
    assert actual["native_binary"] == str(native)
    assert actual["engine_fingerprint"] == "a" * 64
    assert actual["artifact_verified"] is False


def test_python_file_cannot_be_reported_as_a_native_binary(tmp_path, monkeypatch):
    module, provider, pure, _ = installed_pair(tmp_path, monkeypatch)
    provider.__file__ = pure.__file__
    with pytest.raises(RuntimeError, match="native extension"):
        module.runtime_provenance()


def test_foreign_facade_class_is_a_hard_error(tmp_path, monkeypatch):
    module, _, pure, _ = installed_pair(tmp_path, monkeypatch)
    pure.CompiledShapes = object()
    with pytest.raises(RuntimeError, match="shared native"):
        module.runtime_provenance()


def receipted_pair(tmp_path, monkeypatch):
    module, provider, pure, native = installed_pair(tmp_path, monkeypatch)
    actual = {
        "rdflib_turbo": {
            "rdflib_turbo/" + native.name: hashlib.sha256(native.read_bytes()).hexdigest()
        },
        "pyshacl_turbo": {
            "pyshacl_turbo/_native.py": hashlib.sha256(Path(pure.__file__).read_bytes()).hexdigest()
        },
    }
    receipt = {
        "installed_provider": {
            "provider": "fixture",
            "fingerprint": "a" * 64,
            "native_member": "rdflib_turbo/" + native.name,
            "payload": dict(actual["rdflib_turbo"]),
        },
        "installed_facade": {
            "payload": dict(actual["pyshacl_turbo"]),
            "package": str(Path(pure.__file__).parent),
        },
    }
    path = tmp_path / "installed-pair.json"
    path.write_text(json.dumps(receipt))
    monkeypatch.setattr(module, "package_payload", lambda name: actual[name])
    monkeypatch.setattr(module.sys, "prefix", str(tmp_path))
    return module, path, actual, receipt, provider


def test_original_pair_receipt_binds_complete_installed_payloads_and_true_dso(
    tmp_path, monkeypatch
):
    module, path, _, _, _ = receipted_pair(tmp_path, monkeypatch)
    actual = module.runtime_provenance(path)
    assert actual["artifact_verified"] is True
    assert actual["installed_pair_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize(
    "damage", ("provider", "facade", "version", "fingerprint", "member", "origin")
)
def test_pair_receipt_rejects_payload_metadata_or_origin_drift(tmp_path, monkeypatch, damage):
    module, path, actual, receipt, _ = receipted_pair(tmp_path, monkeypatch)
    if damage in ("provider", "facade"):
        actual["rdflib_turbo" if damage == "provider" else "pyshacl_turbo"]["extra.py"] = "changed"
    elif damage == "origin":
        monkeypatch.setattr(module.sys, "prefix", str(tmp_path / "other-venv"))
    else:
        field = {"version": "provider", "fingerprint": "fingerprint", "member": "native_member"}[
            damage
        ]
        receipt["installed_provider"][field] = "changed"
        path.write_text(json.dumps(receipt))
    with pytest.raises(RuntimeError, match="original installed pair"):
        module.runtime_provenance(path)
