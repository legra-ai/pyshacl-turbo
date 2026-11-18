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
        members = (
            [
                ("data-shapes-test-suite/tests/example.ttl", b"# shape\n"),
                ("shacl12-test-suite/tests/core/example12.ttl", b"# shape 1.2\n"),
                ("shacl12-test-suite/README.md", b"# SHACL 1.2 test-suite\n"),
                ("shacl12-test-suite/reports/ignored.ttl", b"# not vendored\n"),
                ("LICENSE.md", b"W3C Software and Document License\n"),
            ]
            if "w3c/data-shapes" in url
            else [("test/example.py", b"assert conforms\n")]
        )
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w:gz") as archive:
            for path, content in members:
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


def test_refresh_pins_the_shacl12_suite_with_license_and_checksums(sync):
    sync.main()
    root = sync.ROOT
    inventory = json.loads((root / "tests/suite-sources.json").read_text())
    shacl12 = inventory["w3c12"]
    assert shacl12["files"] == ["LICENSE.md", "README.md", "core/example12.ttl"]
    assert shacl12["url"].endswith("/w3c/data-shapes/tar.gz/" + shacl12["revision"])
    assert shacl12["license"] == "W3C Software and Document License"
    assert shacl12["committed_at"].endswith("Z")
    expected = "".join(
        f"{hashlib.sha256((root / 'tests/w3c12' / name).read_bytes()).hexdigest()}  {name}\n"
        for name in shacl12["files"]
    )
    assert (root / shacl12["sha256sums"]).read_text() == expected
    assert inventory["w3c"]["files"] == ["example.ttl"]
    assert "url" not in inventory["w3c"]


def test_refresh_stops_when_the_correction_does_not_apply(sync):
    patch = sync.ROOT / "vendor/pyshacl-issue-70.patch"
    patch.write_bytes(patch.read_bytes().replace(b"-assert conforms", b"-unexpected source"))
    with pytest.raises(subprocess.CalledProcessError):
        sync.main()
    assert not (sync.ROOT / "tests/suite-sources.json").exists()
