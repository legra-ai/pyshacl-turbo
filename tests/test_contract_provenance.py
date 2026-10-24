"""Compatibility provenance identifies pure source and the actual shared DSO."""

import hashlib
import importlib.util
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
