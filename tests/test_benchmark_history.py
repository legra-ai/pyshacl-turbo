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


def test_history_commit_requires_a_verified_server_signature_and_exact_parent():
    bench = module()
    requests = []

    def client(path, method="GET", payload=None):
        requests.append((path, method, payload))
        if method == "GET":
            if "/git/ref/" in path:
                return {"object": {"sha": "b" * 40}}
            return {
                "sha": "b" * 40,
                "parents": [{"sha": "a" * 40}],
                "commit": {
                    "message": "perf(history): retain measured results",
                    "tree": {"sha": "c" * 40},
                    "verification": {"verified": True},
                },
            }
        return {
            "data": {
                "createCommitOnBranch": {
                    "commit": {"oid": "b" * 40, "signature": {"isValid": True}}
                }
            }
        }

    oid = bench.signed_commit(
        client,
        "owner/repo",
        "benchmark-results",
        "a" * 40,
        "perf(history): retain measured results",
        [{"path": "report.json.gz", "contents": "AA=="}],
        [],
        expected_tree="c" * 40,
    )
    assert oid == "b" * 40
    request = requests[0][2]["variables"]["input"]
    assert request["expectedHeadOid"] == "a" * 40
    assert request["branch"]["branchName"] == "benchmark-results"

    def unsigned(*args, **kwargs):
        return {"data": {"createCommitOnBranch": {"commit": {"oid": "b" * 40, "signature": None}}}}

    with pytest.raises(RuntimeError, match="verified"):
        bench.signed_commit(
            unsigned,
            "owner/repo",
            "benchmark-results",
            "a" * 40,
            "perf(history): retain measured results",
            [],
            [],
            expected_tree="c" * 40,
        )


def test_missing_history_branch_cannot_fall_back_to_unsigned_or_source_commits(
    tmp_path, monkeypatch
):
    import sys

    bench = module()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "history",
            "--artifacts",
            str(tmp_path),
            "--repository",
            "owner/repo",
            "--run-id",
            "123-1",
            "--run-url",
            "https://github.com/owner/repo/actions/runs/123",
        ],
    )
    monkeypatch.setattr(bench, "run", lambda *args: "")

    def forbidden(*args, **kwargs):
        raise AssertionError("Missing initialization must not mutate GitHub")

    monkeypatch.setattr(bench, "api", forbidden)
    with pytest.raises(RuntimeError, match="Initialize the signed"):
        bench.main()
