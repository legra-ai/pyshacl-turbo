"""An export-only Git declaration never impersonates a registry product."""

import copy
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


def helper():
    path = Path(__file__).resolve().parents[1] / "scripts/published_peers.py"
    spec = importlib.util.spec_from_file_location("published_peers", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def declaration(tmp_path):
    return {
        "role": "uv-export-declaration",
        "project": "pyshacl-turbo",
        "version": "0.7.0",
        "source": str(tmp_path / "original-source"),
        "authority": {
            "kind": "git",
            "repository": "https://github.com/legra-ai/pyshacl-turbo",
            "revision": "a" * 40,
            "files": {"pyproject.toml": "b" * 64},
            "modes": {"pyproject.toml": "100644"},
        },
        "archive": str(tmp_path / "original.tar.gz"),
        "archive_sha256": "c" * 64,
        "archive_files": {"pyproject.toml": "b" * 64},
        "build": {"command": ["uv", "build", "--sdist", "--no-sources"]},
    }


def test_prepare_uses_only_the_verified_owners_declaration_builder(tmp_path, monkeypatch):
    module = helper()
    record = declaration(tmp_path)
    calls = []
    owner, output = tmp_path / "owner", tmp_path / "export-authority"

    def prepare(actual_owner, actual_output, python):
        calls.append(("prepare", actual_owner, actual_output, python))
        return copy.deepcopy(record)

    def verify(actual_owner, actual, *, initial):
        assert actual == record
        calls.append(("verify", actual_owner, initial))

    monkeypatch.setattr(module, "locked_version", lambda *args: "0.7.0")
    monkeypatch.setattr(
        module, "load_declaration", lambda actual: SimpleNamespace(prepare=prepare, verify=verify)
    )
    monkeypatch.setattr(module, "original_peer", lambda *args: pytest.fail("Registry guessed"))
    assert module.prepare_declaration_peer(owner, output) == record
    assert calls == [("prepare", owner, output, sys.executable), ("verify", owner, True)]


@pytest.mark.parametrize("defect", ["registry-kind", "installed-role", "wrong-version"])
def test_wrong_authority_role_or_lock_version_fails_without_registry_fallback(
    tmp_path, monkeypatch, defect
):
    module = helper()
    record = declaration(tmp_path)
    if defect == "registry-kind":
        record["authority"] = {"kind": "published-sdist"}
    elif defect == "installed-role":
        record["role"] = "installed-facade"
    else:
        record["version"] = "0.6.5"
    monkeypatch.setattr(module, "locked_version", lambda *args: "0.7.0")
    monkeypatch.setattr(
        module, "load_declaration", lambda *args: pytest.fail("Wrong typed role was accepted")
    )
    with pytest.raises(ValueError, match="declaration"):
        module.verify_declaration_peer(tmp_path, record)


def test_missing_owner_declaration_support_is_a_hard_capability_error(tmp_path, monkeypatch):
    module = helper()
    monkeypatch.setattr(module, "original_peer", lambda *args: pytest.fail("Registry fallback"))
    with pytest.raises((FileNotFoundError, ValueError)):
        module.prepare_declaration_peer(tmp_path / "owner", tmp_path / "output")


def test_after_export_reattestation_uses_original_archive_and_raw_git_authority(
    tmp_path, monkeypatch
):
    module = helper()
    record = declaration(tmp_path)
    calls = []

    def verify(owner, actual, *, initial):
        assert actual["archive_sha256"] == "c" * 64
        assert actual["authority"]["files"] == {"pyproject.toml": "b" * 64}
        calls.append(initial)
        raise ValueError("Original declaration source bytes changed")

    monkeypatch.setattr(module, "locked_version", lambda *args: "0.7.0")
    monkeypatch.setattr(module, "load_declaration", lambda *args: SimpleNamespace(verify=verify))
    with pytest.raises(ValueError, match="source bytes changed"):
        module.verify_declaration_peer(tmp_path, record, initial=False)
    assert calls == [False]
