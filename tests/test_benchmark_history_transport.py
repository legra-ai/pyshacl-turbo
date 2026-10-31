"""Signed history transport is bounded without publishing partial mutable state."""

import base64
import json
import random
import sys
from pathlib import Path

import pytest
from test_benchmark_history import artifacts, module

MUTABLE = {
    ".benchmark-history-format.json",
    "README.md",
    "history.json",
    "latest-ubuntu-latest.json.gz",
    "latest-ubuntu-latest.md",
    "latest-macos-latest.json.gz",
    "latest-macos-latest.md",
}
HEAD = "a" * 40
MESSAGE = "perf(history): record measured pipeline run 123-1"


def files():
    return [
        {"path": f"runs/123-1/ubuntu-latest/locks/part-{index}-Ω", "contents": "A" * 1800}
        for index in range(4)
    ] + [{"path": name, "contents": "AA=="} for name in sorted(MUTABLE)]


def payload_size(bench, additions):
    payload = bench.commit_payload("owner/repo", "benchmark-results", HEAD, MESSAGE, additions, [])
    return len(json.dumps(payload).encode("utf-8"))


def client(limit, *, fail_at=None, unsigned_at=None, race_at=None):
    state = {"head": HEAD, "requests": [], "mutable_written": False, "files": {}}

    def execute(path, method="GET", payload=None):
        if method == "GET":
            if "/git/ref/" in path:
                return {"object": {"sha": state["head"]}}
            return {
                "sha": state["head"],
                "parents": [{"sha": state["requests"][-1]["expectedHeadOid"]}],
                "commit": {
                    "message": MESSAGE,
                    "tree": {"sha": "c" * 40},
                    "verification": {"verified": True},
                },
            }
        assert len(json.dumps(payload).encode("utf-8")) <= limit
        request = payload["variables"]["input"]
        index = len(state["requests"])
        if race_at == index:
            state["head"] = "f" * 40
        if request["expectedHeadOid"] != state["head"]:
            raise RuntimeError("expected parent moved")
        state["requests"].append(request)
        if index == fail_at:
            raise RuntimeError("transport failed")
        state["head"] = f"{index + 1:040x}"
        for addition in request["fileChanges"]["additions"]:
            state["files"][addition["path"]] = addition["contents"]
            state["mutable_written"] |= addition["path"] in MUTABLE
        return {
            "data": {
                "createCommitOnBranch": {
                    "commit": {
                        "oid": state["head"],
                        "signature": {"isValid": index != unsigned_at},
                    }
                }
            }
        }

    return execute, state


def publish(bench, execute, additions, limit):
    return bench.publish_additions(
        execute,
        "owner/repo",
        "benchmark-results",
        HEAD,
        MESSAGE,
        additions,
        "123-1",
        prepare_tree=lambda base, batch: "c" * 40,
        max_bytes=limit,
    )


def test_bounded_requests_keep_every_file_and_all_mutable_aliases_last():
    bench, additions = module(), files()
    limit = max(payload_size(bench, [item]) for item in additions) + 50
    execute, state = client(limit)
    final = publish(bench, execute, additions, limit)
    assert final == state["head"]
    assert len(state["requests"]) > 2
    assert state["files"] == {item["path"]: item["contents"] for item in additions}
    assert {item["path"] for item in state["requests"][-1]["fileChanges"]["additions"]} == MUTABLE
    assert all(
        item["path"].startswith("runs/123-1/")
        for request in state["requests"][:-1]
        for item in request["fileChanges"]["additions"]
    )


@pytest.mark.parametrize("invalid", ["later_oversized", "mutable_group", "missing", "duplicate"])
def test_invalid_complete_plan_fails_before_any_write(invalid):
    bench, additions = module(), files()
    limit = 6000
    if invalid == "later_oversized":
        additions.append({"path": "runs/123-1/late", "contents": "X" * 10000})
    elif invalid == "mutable_group":
        for item in additions:
            if item["path"] in MUTABLE:
                item["contents"] = "X" * 1000
    elif invalid == "missing":
        additions = [item for item in additions if item["path"] != "history.json"]
    else:
        additions.append(additions[0])
    execute, state = client(limit)
    with pytest.raises(ValueError):
        publish(bench, execute, additions, limit)
    assert state["requests"] == []
    assert not state["mutable_written"]


@pytest.mark.parametrize("failure", ["transport", "signature", "parent"])
def test_intermediate_failure_stops_without_mutable_publication(failure):
    bench, additions = module(), files()
    limit = max(payload_size(bench, [item]) for item in additions) + 50
    settings = {
        "transport": {"fail_at": 1},
        "signature": {"unsigned_at": 1},
        "parent": {"race_at": 1},
    }
    execute, state = client(limit, **settings[failure])
    with pytest.raises(RuntimeError):
        publish(bench, execute, additions, limit)
    assert not state["mutable_written"]


def test_final_signature_failure_is_reported_without_claiming_rollback():
    bench, additions = module(), files()
    limit = payload_size(bench, additions)
    execute, state = client(limit, unsigned_at=1)
    with pytest.raises(RuntimeError, match="verified"):
        publish(bench, execute, additions, limit)
    assert state["mutable_written"]  # The final mutation already wrote; no rollback exists.


def test_main_uses_bounded_signed_transport_for_complete_reports(tmp_path, monkeypatch):
    bench = module()
    source, staged = tmp_path / "input", tmp_path / "size-only"
    artifacts(source)
    for report in source.glob("*/releases.json"):
        data = json.loads(report.read_text())
        data["noise"] = random.Random(0).randbytes(12000).hex()
        report.write_text(json.dumps(data))
    bench.stage_reports(source, staged, "123-1", "https://github.com/owner/repo/actions/runs/123")
    (staged / ".benchmark-history-format.json").write_text(json.dumps(bench.FORMAT))
    additions = bench.additions(staged, "123-1")
    immutable = [item for item in additions if item["path"].startswith("runs/")]
    mutable = [item for item in additions if item["path"] in MUTABLE]
    limit = max(payload_size(bench, immutable), payload_size(bench, mutable)) + 100
    assert payload_size(bench, additions) > limit
    execute, state = client(limit)

    def run(*arguments):
        if arguments[1] == "ls-remote":
            return HEAD + " refs/heads/benchmark-results"
        if arguments[1] == "clone":
            checkout = Path(arguments[-1])
            checkout.mkdir()
            (checkout / ".benchmark-history-format.json").write_text(json.dumps(bench.FORMAT))
            return ""
        assert arguments[-2:] == ("rev-parse", "HEAD")
        return HEAD

    monkeypatch.setattr(bench, "run", run)
    monkeypatch.setattr(bench, "api", execute)
    monkeypatch.setattr(bench, "expected_tree", lambda checkout, base, batch: "c" * 40)
    monkeypatch.setattr(bench, "MAX_COMMIT_REQUEST_BYTES", limit, raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "history",
            "--artifacts",
            str(source),
            "--repository",
            "owner/repo",
            "--run-id",
            "123-1",
            "--run-url",
            "https://github.com/owner/repo/actions/runs/123",
        ],
    )
    bench.main()
    assert len(state["requests"]) == 2
    assert state["files"] == {item["path"]: item["contents"] for item in additions}
    for item in additions:
        assert (
            base64.b64decode(state["files"][item["path"]]) == (staged / item["path"]).read_bytes()
        )
