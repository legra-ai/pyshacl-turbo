"""Release tests consume explicit original metadata, never candidate dependency pins."""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import socket
import tarfile
from pathlib import Path

import pytest


def helper():
    path = Path(__file__).resolve().parents[1] / "scripts/release_project_inputs.py"
    spec = importlib.util.spec_from_file_location("release_project_inputs", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(data):
    return hashlib.sha256(data).hexdigest()


def authority(tmp_path):
    base = tmp_path / "original"
    base.mkdir()
    contents = {
        "pyproject.toml": b'[project]\nname="pyshacl-turbo"\nversion="0.7.0"\n',
        "uv.lock": b"version=1\n",
        "PKG-INFO": b"Name: pyshacl-turbo\nVersion: 0.7.0\n",
        "tests/retained.py": b"original test bytes\n",
    }
    archive = tmp_path / "original.tar.gz"
    with tarfile.open(archive, "w:gz") as output:
        for name, data in contents.items():
            member = tarfile.TarInfo("pyshacl_turbo-0.7.0/" + name)
            member.size = len(data)
            output.addfile(member, io.BytesIO(data))
            target = base / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    hashes = {name: digest(data) for name, data in contents.items()}
    record = {
        "schema": 1,
        "kind": "original-facade-release-metadata",
        "project": "pyshacl-turbo",
        "source": str(base),
        "base_revision": "a" * 40,
        "archive": str(archive),
        "archive_sha256": digest(archive.read_bytes()),
        "archive_files": hashes,
        "version": "0.7.0",
    }
    record_path = tmp_path / "authority.json"
    record_path.write_text(json.dumps(record))
    receipt = tmp_path / "candidate-inputs.json"
    receipt.write_text(
        json.dumps(
            {
                "schema": 1,
                "kind": "test-only-facade-candidate",
                "publishable": False,
                "artifact_namespace": "candidate-facade",
                "base_input": {"revision": "a" * 40, "files": hashes},
                "base_archive": archive.name,
                "base_archive_sha256": record["archive_sha256"],
            }
        )
    )
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "pyproject.toml").write_text(
        '[project]\nname="pyshacl-turbo"\nversion="0.7.0+candidate.test"\n'
        'dependencies=["rdflib-turbo==0.2.0a999"]\n'
    )
    (candidate / "uv.lock").write_text("candidate dependency-bound lock\n")
    environment = {
        "SHACL_CANDIDATE_RECEIPT": str(receipt),
        "SHACL_BASE_REVISION": "a" * 40,
        "SHACL_RELEASE_PROJECT_AUTHORITY": str(record_path),
    }
    return candidate, base, record_path, environment


def test_non_candidate_uses_only_its_own_original_metadata(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname="pyshacl-turbo"\nversion="0.7.0"\n')
    (tmp_path / "uv.lock").write_bytes(b"original lock bytes\n")
    assert helper().read_release_metadata(tmp_path, {}) == {
        name: (tmp_path / name).read_bytes() for name in ("pyproject.toml", "uv.lock")
    }


def test_candidate_requires_explicit_original_authority(tmp_path):
    candidate, _, _, environment = authority(tmp_path)
    del environment["SHACL_RELEASE_PROJECT_AUTHORITY"]
    with pytest.raises(ValueError, match="original.*authority"):
        helper().read_release_metadata(candidate, environment)
    with pytest.raises(ValueError, match="original.*authority"):
        helper().read_release_metadata(candidate, {})


def test_verified_original_is_read_without_rewriting_candidate_or_original(tmp_path):
    candidate, base, _, environment = authority(tmp_path)
    before = {str(path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    assert helper().read_release_metadata(candidate, environment) == {
        name: (base / name).read_bytes() for name in ("pyproject.toml", "uv.lock")
    }
    assert {
        str(path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()
    } == before


@pytest.mark.parametrize(
    "damage",
    [
        "archive",
        "source",
        "extra-source",
        "inventory",
        "revision",
        "version",
        "receipt-sha",
        "declaration-peer",
    ],
)
def test_original_metadata_authority_rejects_changed_or_substituted_inputs(tmp_path, damage):
    candidate, base, record_path, environment = authority(tmp_path)
    record = json.loads(record_path.read_text())
    receipt = Path(environment["SHACL_CANDIDATE_RECEIPT"])
    if damage == "archive":
        Path(record["archive"]).write_bytes(b"changed archive")
    elif damage == "source":
        (base / "tests/retained.py").write_bytes(b"changed tests")
    elif damage == "extra-source":
        (base / "unrecorded.txt").write_bytes(b"unexpected file")
    elif damage == "inventory":
        del record["archive_files"]["PKG-INFO"]
    elif damage == "revision":
        record["base_revision"] = "b" * 40
    elif damage == "version":
        record["version"] = "0.8.0"
    elif damage == "receipt-sha":
        value = json.loads(receipt.read_text())
        value["base_archive_sha256"] = "0" * 64
        receipt.write_text(json.dumps(value))
    elif damage == "declaration-peer":
        alternate = tmp_path / "declaration.tar.gz"
        alternate.write_bytes(Path(record["archive"]).read_bytes())
        record["archive"] = str(alternate)
    record_path.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        helper().read_release_metadata(candidate, environment)


def test_source_links_cannot_hide_changed_metadata(tmp_path):
    candidate, base, _, environment = authority(tmp_path)
    original = base / "uv.lock"
    external = tmp_path / "external.lock"
    external.write_bytes(original.read_bytes())
    original.unlink()
    original.symlink_to(external)
    with pytest.raises(ValueError, match="link"):
        helper().read_release_metadata(candidate, environment)


@pytest.mark.skipif(os.name != "posix", reason="POSIX FIFO and Unix socket source entries")
@pytest.mark.parametrize("kind", ["fifo", "socket"])
def test_complete_original_inventory_rejects_extra_nonregular_entries(tmp_path, kind):
    candidate, base, _, environment = authority(tmp_path)
    if kind == "fifo":
        os.mkfifo(base / "unexpected-entry")
        with pytest.raises(ValueError, match="nonregular"):
            helper().read_release_metadata(candidate, environment)
    else:
        # Relative bind avoids the platform's short Unix-domain socket path limit.
        with socket.socket(socket.AF_UNIX) as listener, contextlib.chdir(base):
            listener.bind("unexpected-entry")
            with pytest.raises(ValueError, match="nonregular"):
                helper().read_release_metadata(candidate, environment)
