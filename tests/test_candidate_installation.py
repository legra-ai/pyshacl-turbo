"""Candidate wheel installation is explicit and remains distinct from registry proof."""

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def helper():
    spec = importlib.util.spec_from_file_location(
        "registry_pair", ROOT / "scripts/check_registry_pair.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_probe(code, direct):
    fixture = "import importlib.metadata,json; from types import SimpleNamespace; "
    fixture += f"record = {json.dumps(direct)!r}; "
    fixture += "importlib.metadata.distribution = lambda name: SimpleNamespace(read_text=lambda filename: record if record != 'null' else None)\n"
    result = subprocess.run(
        [sys.executable, "-I", "-c", fixture + code], capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr)


def execute(module, mode, direct, wheel=None):
    run_probe(
        module.installation_probe(
            mode,
            wheel,
            hashlib.sha256(wheel.read_bytes()).hexdigest() if wheel is not None else None,
        ),
        direct,
    )


def test_registry_mode_still_rejects_every_direct_wheel(tmp_path):
    module = helper()
    with pytest.raises(RuntimeError, match="direct URL"):
        execute(module, module.InstallationMode.REGISTRY, {"url": "file:///candidate.whl"})
    execute(module, module.InstallationMode.REGISTRY, None)


def test_candidate_requires_exact_local_url_and_original_archive_hash(tmp_path):
    module = helper()
    wheel = tmp_path / "actual original.whl"
    wheel.write_bytes(b"original fixture archive")
    direct = {
        "url": wheel.as_uri(),
        "archive_info": {"hashes": {"sha256": hashlib.sha256(wheel.read_bytes()).hexdigest()}},
    }
    execute(module, module.InstallationMode.CANDIDATE, direct, wheel)
    execute(
        module,
        module.InstallationMode.CANDIDATE,
        {"url": wheel.as_uri(), "archive_info": {}},
        wheel,
    )
    for bad in (
        None,
        {**direct, "url": "https://example.invalid/other.whl"},
        {**direct, "archive_info": {"hashes": {"sha256": "0" * 64}}},
        {**direct, "dir_info": {"editable": True}},
    ):
        with pytest.raises(RuntimeError, match="original candidate wheel"):
            execute(module, module.InstallationMode.CANDIDATE, bad, wheel)


def test_no_automatic_mode_or_candidate_source_guessing(tmp_path):
    module = helper()
    with pytest.raises(TypeError, match="explicit installation mode"):
        module.installation_probe("candidate")
    with pytest.raises(ValueError, match="original native wheel"):
        module.installation_probe(module.InstallationMode.CANDIDATE)
    with pytest.raises(ValueError, match="Registry mode"):
        module.installation_probe(module.InstallationMode.REGISTRY, tmp_path / "wheel.whl")


def test_original_wheel_change_after_request_is_rejected(tmp_path):
    module = helper()
    wheel = tmp_path / "original.whl"
    wheel.write_bytes(b"original")
    code = module.installation_probe(
        module.InstallationMode.CANDIDATE, wheel, hashlib.sha256(b"original").hexdigest()
    )
    direct = {"url": wheel.as_uri(), "archive_info": {}}
    wheel.write_bytes(b"changed after request")
    with pytest.raises(RuntimeError, match="original candidate wheel"):
        run_probe(code, direct)
