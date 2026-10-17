"""Only complete successful platform measurements enter public history."""

import gzip
import importlib.util
import json
from pathlib import Path

import pytest


def module():
    path = Path(__file__).resolve().parents[1] / "scripts/benchmark_history.py"
    spec = importlib.util.spec_from_file_location("benchmark_history", path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def artifacts(root):
    for platform in ("ubuntu-latest", "macos-latest"):
        directory = root / f"pipeline-reports-{platform}"
        directory.mkdir(parents=True)
        data = {
            "schema": 1,
            "date": "2026-10-17T00:00:00+00:00",
            "source_revision": "a" * 40,
            "environments": {
                "candidate": {"identity": {"packages": {"pyshacl-turbo": {"version": "1.0.0"}}}}
            },
            "runs": [{"mode": "rdfs"}],
        }
        (directory / "releases.json").write_text(json.dumps(data))
        (directory / "releases.md").write_text("Measured report\n")
        (directory / "locks/candidate").mkdir(parents=True)
        (directory / "locks/candidate/uv.lock").write_text("version = 1\n")
        (directory / "unwanted-secret.env").write_text("must not publish")


def test_history_preserves_raw_measurements_locks_and_previous_runs(tmp_path):
    bench = module()
    source, destination = tmp_path / "input", tmp_path / "history"
    artifacts(source)
    bench.stage_reports(source, destination, "123-1", "https://github.com/example/run/123")
    bench.stage_reports(source, destination, "124-1", "https://github.com/example/run/124")
    assert len(json.loads((destination / "history.json").read_text())) == 4
    raw = destination / "runs/123-1/ubuntu-latest/releases.json.gz"
    assert json.loads(gzip.decompress(raw.read_bytes()))["source_revision"] == "a" * 40
    assert (destination / "runs/123-1/macos-latest/locks/candidate/uv.lock").exists()
    assert not list(destination.rglob("*.env"))
    assert "runs/124-1" in (destination / "README.md").read_text()
    with pytest.raises(ValueError, match="exists"):
        bench.stage_reports(source, destination, "124-1", "https://github.com/example/run/124")


def test_failed_or_missing_platforms_cannot_replace_published_measurements(tmp_path):
    bench = module()
    source, destination = tmp_path / "input", tmp_path / "history"
    artifacts(source)
    file = source / "pipeline-reports-macos-latest/releases.json"
    data = json.loads(file.read_text())
    data["error"] = "worker crashed"
    file.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="failed"):
        bench.stage_reports(source, destination, "123-1", "https://github.com/example/run/123")
    assert not destination.exists()
