"""Refreshing upstream sources must retain reviewed local test corrections."""

import hashlib
import importlib.util
import io
import json
import subprocess
import tarfile
from pathlib import Path

import pytest


@pytest.fixture
def sync(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[1] / "scripts/sync_suites.py"
    spec = importlib.util.spec_from_file_location("sync_suites", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    (tmp_path / "vendor").mkdir()
    (tmp_path / "vendor/pyshacl-issue-70.patch").write_bytes(
        b"diff --git a/vendor/pyshacl/test/example.py b/vendor/pyshacl/test/example.py\n"
        b"--- a/vendor/pyshacl/test/example.py\n"
        b"+++ b/vendor/pyshacl/test/example.py\n"
        b"@@ -1 +1 @@\n"
        b"-assert conforms\n"
        b"+assert not conforms\n"
    )

    def download(url, timeout):
        path, content = (
            ("data-shapes-test-suite/tests/example.ttl", b"# shape\n")
            if "w3c/data-shapes" in url
            else ("test/example.py", b"assert conforms\n")
        )
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w:gz") as archive:
            member = tarfile.TarInfo("upstream/" + path)
            member.size = len(content)
            archive.addfile(member, io.BytesIO(content))
        stream.seek(0)
        return stream

    monkeypatch.setattr(module.urllib.request, "urlopen", download)
    return module


def test_refresh_applies_and_records_the_local_correction(sync):
    sync.main()
    root = sync.ROOT
    assert (root / "vendor/pyshacl/test/example.py").read_text() == "assert not conforms\n"
    inventory = json.loads((root / "tests/suite-sources.json").read_text())
    patch = "vendor/pyshacl-issue-70.patch"
    assert inventory["pyshacl"]["local_patches"] == [
        {"path": patch, "sha256": hashlib.sha256((root / patch).read_bytes()).hexdigest()}
    ]


def test_refresh_stops_when_the_correction_does_not_apply(sync):
    patch = sync.ROOT / "vendor/pyshacl-issue-70.patch"
    patch.write_bytes(patch.read_bytes().replace(b"-assert conforms", b"-unexpected source"))
    with pytest.raises(subprocess.CalledProcessError):
        sync.main()
    assert not (sync.ROOT / "tests/suite-sources.json").exists()
