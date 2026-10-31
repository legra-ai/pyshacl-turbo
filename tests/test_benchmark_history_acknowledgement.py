"""A lost mutation acknowledgement never substitutes for an exact signed tree."""

import base64

import pytest
from test_benchmark_history import module
from test_benchmark_history_transport import MESSAGE, MUTABLE


def repository(tmp_path):
    bench = module()
    root = tmp_path / "history"
    root.mkdir()
    bench.run("git", "init", "--quiet", root)
    for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid")):
        bench.run("git", "-C", root, "config", key, value)
    for name in (*sorted(MUTABLE), "older/retained.txt"):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("previous " + name)
    bench.run("git", "-C", root, "add", ".")
    tree = bench.run("git", "-C", root, "write-tree")
    head = bench.run("git", "-C", root, "commit-tree", tree, "-m", "fixture base")
    bench.run("git", "-C", root, "update-ref", "HEAD", head)
    return bench, root, head


def addition(path, contents):
    return {"path": path, "contents": base64.b64encode(contents).decode("ascii")}


def server(bench, root, head, *, fault=None, acknowledge=False):
    state = {"head": head, "mutations": [], "reads": [], "verified": [], "commits": {}}

    def execute(path, method="GET", payload=None):
        if path == "graphql":
            request = payload["variables"]["input"]
            assert request["expectedHeadOid"] == state["head"]
            # A second mutation must not run until the first whole commit was read back.
            if state["mutations"]:
                assert state["verified"][-1] == state["head"]
            state["mutations"].append(request)
            if fault == "unchanged":
                raise bench.HistoryTransportError("HTTP 504")
            tree = bench.expected_tree(root, state["head"], request["fileChanges"]["additions"])
            parent, message = state["head"], request["message"]["headline"]
            if fault == "tree":
                tree = bench.expected_tree(root, tree, [addition("README.md", b"foreign alias")])
            if fault == "parent":
                parent = "f" * 40
            if fault == "message":
                message = "foreign message"
            oid = f"{len(state['mutations']):040x}"
            state["commits"][oid] = {
                "sha": oid,
                "parents": [{"sha": parent}],
                "commit": {
                    "message": message,
                    "tree": {"sha": tree},
                    "verification": {"verified": fault != "unsigned"},
                },
            }
            state["head"] = oid
            if not acknowledge:
                raise bench.HistoryTransportError("HTTP 504 after server committed")
            return {
                "data": {
                    "createCommitOnBranch": {"commit": {"oid": oid, "signature": {"isValid": True}}}
                }
            }
        state["reads"].append(path)
        if fault == "unreadable":
            raise bench.HistoryTransportError("readback unavailable")
        if "/git/ref/" in path:
            return {"object": {"sha": state["head"]}}
        commit = state["commits"][path.rsplit("/", 1)[1]]
        state["verified"].append(commit["sha"])
        return commit

    return execute, state


@pytest.mark.parametrize("acknowledge", [False, True])
def test_exact_whole_tree_is_required_before_the_next_mutable_batch(tmp_path, acknowledge):
    bench, root, head = repository(tmp_path)
    immutable = [addition("runs/123-1/facts.bin", b"\x00\xffcomplete facts")]
    mutable = [addition(name, ("new " + name).encode()) for name in sorted(MUTABLE)]
    expected = bench.expected_tree(root, head, immutable)
    # The first expected tree includes the untouched aliases AND unrelated old history.
    assert bench.run("git", "-C", root, "show", expected + ":README.md") == "previous README.md"
    assert (
        bench.run("git", "-C", root, "show", expected + ":older/retained.txt")
        == "previous older/retained.txt"
    )
    execute, state = server(bench, root, head, acknowledge=acknowledge)
    # The fake server keeps real trees while its signed commit OIDs are intentionally synthetic.
    trees = iter([expected, bench.expected_tree(root, expected, mutable)])
    original = bench.expected_tree

    def prepare(base, additions):
        return next(trees)

    def existing_tree(checkout, base, additions):
        if base in state["commits"]:
            base = state["commits"][base]["commit"]["tree"]["sha"]
        return original(checkout, base, additions)

    bench.expected_tree = existing_tree
    final = bench.publish_additions(
        execute,
        "owner/repo",
        "benchmark-results",
        head,
        MESSAGE,
        immutable + mutable,
        "123-1",
        prepare_tree=prepare,
    )
    assert final == state["head"]
    assert len(state["mutations"]) == 2  # No mutation retry, even after HTTP 504.
    assert state["verified"] == ["0" * 39 + "1", "0" * 39 + "2"]
    assert {x["path"] for x in state["mutations"][-1]["fileChanges"]["additions"]} == MUTABLE


@pytest.mark.parametrize(
    "fault", ["tree", "parent", "message", "unsigned", "unchanged", "unreadable"]
)
@pytest.mark.parametrize("acknowledge", [False, True])
def test_foreign_or_indeterminate_state_never_advances_to_aliases(tmp_path, fault, acknowledge):
    bench, root, head = repository(tmp_path)
    additions = [addition("runs/123-1/facts", b"facts")]
    execute, state = server(bench, root, head, fault=fault, acknowledge=acknowledge)
    tree = bench.expected_tree(root, head, additions)
    with pytest.raises(RuntimeError):
        bench.signed_commit(
            execute,
            "owner/repo",
            "benchmark-results",
            head,
            MESSAGE,
            additions,
            [],
            expected_tree=tree,
        )
    assert len(state["mutations"]) == 1


def test_tree_preparation_does_not_change_the_clone_index_or_working_tree(tmp_path):
    bench, root, head = repository(tmp_path)
    index = (root / ".git/index").read_bytes()
    before = {
        p.relative_to(root): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and ".git" not in p.parts
    }
    change = [addition("runs/123-1/unicode-Ω", b"\x00\xffpayload")]
    first = bench.expected_tree(root, head, change)
    second = bench.expected_tree(root, head, change)
    assert first == second
    assert (root / ".git/index").read_bytes() == index
    assert before == {
        p.relative_to(root): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and ".git" not in p.parts
    }
    assert bench.run("git", "-C", root, "status", "--porcelain") == ""
