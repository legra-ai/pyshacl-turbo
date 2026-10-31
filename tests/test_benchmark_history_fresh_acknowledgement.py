"""Read-after-write acknowledgement may lag a successful signed mutation."""

import pytest
from test_benchmark_history_acknowledgement import addition, repository, server
from test_benchmark_history_transport import MESSAGE


@pytest.mark.parametrize("acknowledge", [False, True])
def test_stale_old_tip_is_rechecked_without_repeating_the_write(tmp_path, monkeypatch, acknowledge):
    bench, root, head = repository(tmp_path)
    changes = [addition("runs/123-1/facts", b"complete facts")]
    execute, state = server(bench, root, head, acknowledge=acknowledge)
    reads = []

    def stale(path, method="GET", payload=None):
        if "/git/ref/" in path:
            reads.append(path)
            if len(reads) < 3:
                return {"object": {"sha": head}}
        return execute(path, method, payload)

    monkeypatch.setattr(bench, "sleep", lambda seconds: None, raising=False)
    result = bench.signed_commit(
        stale,
        "owner/repo",
        "benchmark-results",
        head,
        MESSAGE,
        changes,
        [],
        expected_tree=bench.expected_tree(root, head, changes),
    )
    assert result == state["head"]
    assert len(state["mutations"]) == 1
    assert len(reads) == 3
    assert state["verified"] == [result]


def test_fresh_ref_requests_require_cache_revalidation(monkeypatch):
    from test_benchmark_history import module

    bench = module()
    requests = []

    def command(arguments, payload=None):
        requests.append(arguments)
        return '{"object":{"sha":"current"}}'

    monkeypatch.setattr(bench, "command", command)
    bench.api("repos/owner/repo/git/ref/heads/benchmark-results")
    assert "Cache-Control: no-cache" in requests[0]
    assert "Pragma: no-cache" in requests[0]


@pytest.mark.parametrize("foreign", [False, True])
def test_never_acknowledged_or_foreign_tip_cannot_accept_an_existing_commit(
    tmp_path, monkeypatch, foreign
):
    bench, root, head = repository(tmp_path)
    changes = [addition("runs/123-1/facts", b"complete facts")]
    execute, state = server(bench, root, head, acknowledge=True)
    reads, delays = [], []

    def stale(path, method="GET", payload=None):
        if "/git/ref/" in path:
            reads.append(path)
            return {"object": {"sha": "f" * 40 if foreign else head}}
        return execute(path, method, payload)

    monkeypatch.setattr(bench, "sleep", delays.append)
    with pytest.raises(RuntimeError, match="no exact current branch acknowledgement"):
        bench.signed_commit(
            stale,
            "owner/repo",
            "benchmark-results",
            head,
            MESSAGE,
            changes,
            [],
            expected_tree=bench.expected_tree(root, head, changes),
        )
    assert len(state["mutations"]) == 1
    assert len(state["commits"]) == 1  # Mere existence never constitutes acknowledgement.
    assert state["verified"] == []
    assert len(reads) == (1 if foreign else 7)
    assert delays == ([] if foreign else [1, 2, 4, 8, 16, 32])
