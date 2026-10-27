"""A candidate project cannot silently resolve one product from another source."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def helper():
    spec = importlib.util.spec_from_file_location(
        "benchmark_candidate", ROOT / "scripts/benchmark_candidate.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_candidate_uv_lock_requires_all_three_exact_original_wheel_paths(tmp_path):
    module = helper()
    wheels = {
        name: tmp_path / (name + ".whl")
        for name in ("rdflib-turbo", "pyshacl-turbo", "owlrl-turbo")
    }
    lock = {
        "package": [{"name": name, "source": {"path": str(path)}} for name, path in wheels.items()]
    }
    module.verify_lock(lock, tmp_path, wheels)
    lock["package"][0]["source"] = {"registry": "https://pypi.org/simple"}
    with pytest.raises(ValueError, match="exact original wheel"):
        module.verify_lock(lock, tmp_path, wheels)
    lock["package"] = lock["package"][1:]
    with pytest.raises(ValueError, match="exact original wheel"):
        module.verify_lock(lock, tmp_path, wheels)


def test_candidate_probe_reuses_full_class_store_and_original_payload_checks(tmp_path):
    module = helper()
    wheel = tmp_path / "native.whl"
    wheel.write_bytes(b"actual file fixture")
    code = module.probe(tmp_path / "owner", tmp_path / "facade.whl", wheel, tmp_path / "project")
    assert "Registry Store did not produce the expected violation" in code
    assert "Registry transaction validation missed its pending write" in code
    assert "Facade classes do not belong" in code
    assert "verify_loaded_facade" in code
    assert "exact original candidate wheel" in code
    assert "owlrl_turbo" in code
    assert "loaded outside" in code
