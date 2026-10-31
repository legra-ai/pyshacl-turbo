"""Publish successful measurements to the generated benchmark-results branch."""

import argparse
import base64
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PLATFORMS = {"ubuntu-latest", "macos-latest"}
FORMAT = {"schema": 1, "kind": "turbo-pipeline-history"}
# Below the observed 45 MB endpoint limit; sizes include the complete JSON request.
MAX_COMMIT_REQUEST_BYTES = 40_000_000
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from upstream_support.process_launch import Popen


def stage_reports(artifacts, destination, run_id, run_url):
    if not re.fullmatch(r"[0-9]+-[0-9]+", run_id) or not run_url.startswith("https://github.com/"):
        raise ValueError("Use an explicit GitHub run ID/attempt and run URL")
    if (destination / "runs" / run_id).exists():
        raise ValueError(f"Run already exists: {run_id}")
    reports = {}
    for platform in sorted(PLATFORMS):
        source = artifacts / f"pipeline-reports-{platform}"
        report = json.loads((source / "releases.json").read_text())
        if report.get("error") or report.get("schema") != 1 or not report.get("runs"):
            raise ValueError(f"Cannot publish failed or empty report: {platform}")
        if not (source / "releases.md").is_file() or not (source / "locks").is_dir():
            raise ValueError(f"Incomplete benchmark report: {platform}")
        reports[platform] = (source, report)
    destination.mkdir(parents=True, exist_ok=True)
    history_file = destination / "history.json"
    history = json.loads(history_file.read_text()) if history_file.exists() else []
    for platform, (source, report) in reports.items():
        relative = Path("runs") / run_id / platform
        directory = destination / relative
        directory.mkdir(parents=True)
        shutil.copy2(source / "releases.md", directory / "releases.md")
        shutil.copytree(source / "locks", directory / "locks")
        raw = gzip.compress((source / "releases.json").read_bytes(), mtime=0)
        (directory / "releases.json.gz").write_bytes(raw)
        (destination / f"latest-{platform}.json.gz").write_bytes(raw)
        shutil.copy2(source / "releases.md", destination / f"latest-{platform}.md")
        products = report["environments"]["candidate"]["identity"]["packages"]
        versions = {
            name: value["version"] for name, value in products.items() if name.endswith("-turbo")
        }
        history.append(
            {
                "run_id": run_id,
                "platform": platform,
                "date": report["date"],
                "revision": report["source_revision"],
                "versions": versions,
                "report": (relative / "releases.md").as_posix(),
                "raw": (relative / "releases.json.gz").as_posix(),
                "workflow": run_url,
            }
        )
    history.sort(
        key=lambda value: (value["date"], value["run_id"], value["platform"]), reverse=True
    )
    history_file.write_text(json.dumps(history, indent=2) + "\n")
    lines = [
        "# Companion turbo performance history",
        "",
        "Generated from successful shared-dataset benchmarks. PRs cannot publish here.",
        "Each run compares the original Python trio, the initial turbo releases, the latest compatible published turbo set, and exact candidate wheels.",
        "Timing and whole-process peak RSS are descriptive measurements on shared CI machines. Compare the recorded hardware/platform and full-output parity before interpreting changes.",
        "",
        "| Date | Platform | Candidate versions | Report | Raw evidence | CI run |",
        "|---|---|---|---|---|---|",
    ]
    for entry in history:
        versions = ", ".join(
            f"{name} {version}" for name, version in sorted(entry["versions"].items())
        )
        lines.append(
            f"| {entry['date']} | {entry['platform']} | {versions} | [report]({entry['report']}) | [JSON.gz]({entry['raw']}) | [run]({entry['workflow']}) |"
        )
    (destination / "README.md").write_text("\n".join(lines) + "\n")


class HistoryTransportError(RuntimeError):
    """The mutation command failed without an authoritative acknowledgement."""


def command(arguments, payload=None, *, input_bytes=None, environment=None):
    with Popen(
        list(map(str, arguments)),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=input_bytes is None,
        env=environment,
    ) as process:
        try:
            stdout, stderr = process.communicate(
                input_bytes
                if input_bytes is not None
                else json.dumps(payload)
                if payload is not None
                else None,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise HistoryTransportError("Benchmark history command timed out") from None
        if process.returncode:
            raise HistoryTransportError(f"Benchmark history command failed: {arguments}\n{stderr}")
    return (stdout.decode("utf-8") if isinstance(stdout, bytes) else stdout).strip()


def run(*arguments):
    return command(arguments)


def api(path, method="GET", payload=None):
    arguments = ["gh", "api", path, "--method", method]
    if payload is not None:
        arguments += ["--input", "-"]
    result = command(arguments, payload)
    value = json.loads(result) if result else {}
    if value.get("errors"):
        raise RuntimeError(f"GitHub rejected benchmark publication: {value['errors']}")
    return value


def commit_payload(repository, branch, head, message, additions, deletions):
    query = """mutation($input:CreateCommitOnBranchInput!) {
      createCommitOnBranch(input:$input) { commit { oid signature { isValid } } }
    }"""
    return {
        "query": query,
        "variables": {
            "input": {
                "branch": {"repositoryNameWithOwner": repository, "branchName": branch},
                "expectedHeadOid": head,
                "message": {"headline": message},
                "fileChanges": {
                    "additions": additions,
                    "deletions": [{"path": path} for path in deletions],
                },
            }
        },
    }


def signed_commit(
    client, repository, branch, head, message, additions, deletions, *, expected_tree
):
    acknowledged = None
    try:
        response = client(
            "graphql",
            "POST",
            commit_payload(repository, branch, head, message, additions, deletions),
        )
        commit = response["data"]["createCommitOnBranch"]["commit"]
        if not commit.get("signature") or commit["signature"].get("isValid") is not True:
            raise RuntimeError("GitHub did not return a verified signed history commit")
        acknowledged = commit["oid"]
    except HistoryTransportError:
        # A 504 can follow a successful server mutation. Never retry the write.
        pass
    tip = client(f"repos/{repository}/git/ref/heads/{branch}")["object"]["sha"]
    if tip == head or (acknowledged is not None and tip != acknowledged):
        raise RuntimeError("History mutation has no exact current branch acknowledgement")
    observed = client(f"repos/{repository}/commits/{tip}")
    body = observed["commit"]
    if (
        observed["sha"] != tip
        or [parent["sha"] for parent in observed["parents"]] != [head]
        or body["message"] != message
        or body["tree"]["sha"] != expected_tree
        or body["verification"]["verified"] is not True
    ):
        raise RuntimeError("History commit does not match the exact verified signed postcondition")
    return tip


def expected_tree(checkout, base, additions):
    """Build the whole expected tree with a private index, preserving every other file."""
    with tempfile.TemporaryDirectory(prefix="turbo-history-index-") as temporary:
        environment = {**os.environ, "GIT_INDEX_FILE": str(Path(temporary) / "index")}

        def git(*arguments, input_bytes=None):
            return command(
                ["git", "-C", checkout, *arguments],
                input_bytes=input_bytes,
                environment=environment,
            )

        git("read-tree", base)
        for addition in additions:
            blob = git(
                "hash-object",
                "-w",
                "--stdin",
                input_bytes=base64.b64decode(addition["contents"], validate=True),
            )
            git("update-index", "--add", "--cacheinfo", "100644", blob, addition["path"])
        return git("write-tree")


def publish_additions(
    client,
    repository,
    branch,
    head,
    message,
    files,
    run_id,
    *,
    prepare_tree,
    max_bytes=MAX_COMMIT_REQUEST_BYTES,
):
    mutable_names = {"README.md", "history.json", ".benchmark-history-format.json"}
    mutable_names.update(
        f"latest-{platform}.{suffix}" for platform in PLATFORMS for suffix in ("md", "json.gz")
    )
    immutable, mutable, seen = [], [], set()
    for addition in files:
        path = addition["path"]
        if path in seen:
            raise ValueError(f"Duplicate history file: {path}")
        seen.add(path)
        if path in mutable_names:
            mutable.append(addition)
        elif path.startswith(f"runs/{run_id}/"):
            immutable.append(addition)
        else:
            raise ValueError(f"Unexpected history publication file: {path}")
    if {item["path"] for item in mutable} != mutable_names:
        raise ValueError("History publication requires all seven mutable files")

    def request_bytes(additions):
        payload = commit_payload(repository, branch, head, message, additions, [])
        return len(json.dumps(payload).encode("utf-8"))

    # Preflight the entire plan before even immutable files become visible.
    for addition in files:
        if request_bytes([addition]) > max_bytes:
            raise ValueError(f"History file exceeds the signed request limit: {addition['path']}")
    if request_bytes(mutable) > max_bytes:
        raise ValueError("Mutable history files exceed one atomic signed request")
    batches, batch = [], []
    for addition in immutable:
        candidate = [*batch, addition]
        if request_bytes(candidate) > max_bytes:
            batches.append(batch)
            batch = [addition]
        else:
            batch = candidate
    if batch:
        batches.append(batch)
    batches.append(mutable)
    trees, tree = [], head
    for additions in batches:
        tree = prepare_tree(tree, additions)
        trees.append(tree)
    for additions, tree in zip(batches, trees, strict=True):
        if request_bytes(additions) > max_bytes:
            raise ValueError("History commit exceeds the signed request limit")
        head = signed_commit(
            client, repository, branch, head, message, additions, [], expected_tree=tree
        )
    # Signature verification follows each mutation. A final verification failure
    # is reported, but cannot roll back aliases already written by that mutation.
    return head


def additions(directory, run_id):
    files = list((directory / "runs" / run_id).rglob("*"))
    files += [
        directory / name for name in ("README.md", "history.json", ".benchmark-history-format.json")
    ]
    files += [
        directory / f"latest-{platform}.{suffix}"
        for platform in PLATFORMS
        for suffix in ("md", "json.gz")
    ]
    return [
        {
            "path": path.relative_to(directory).as_posix(),
            "contents": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
        for path in sorted(files)
        if path.is_file()
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True, type=Path)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--output", type=Path, help="Stage locally without GitHub writes")
    args = parser.parse_args()
    if args.output:
        stage_reports(args.artifacts, args.output, args.run_id, args.run_url)
        return
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
        raise ValueError("Expected owner/repository")
    with tempfile.TemporaryDirectory(prefix="turbo-benchmark-history-") as temporary:
        checkout = Path(temporary) / "history"
        url = f"https://github.com/{args.repository}.git"
        exists = bool(run("git", "ls-remote", "--heads", url, "refs/heads/benchmark-results"))
        if not exists:
            raise RuntimeError(
                "Initialize the signed artifact branch with scripts/init_benchmark_history.py before publishing"
            )
        run(
            "git",
            "clone",
            "--depth",
            "1",
            "--single-branch",
            "--branch",
            "benchmark-results",
            url,
            checkout,
        )
        if json.loads((checkout / ".benchmark-history-format.json").read_text()) != FORMAT:
            raise RuntimeError("The benchmark-results branch is not owned by this publisher")
        head = run("git", "-C", checkout, "rev-parse", "HEAD")
        stage_reports(args.artifacts, checkout, args.run_id, args.run_url)
        files = additions(checkout, args.run_id)
        publish_additions(
            api,
            args.repository,
            "benchmark-results",
            head,
            f"perf(history): record measured pipeline run {args.run_id}",
            files,
            args.run_id,
            prepare_tree=lambda base, batch: expected_tree(checkout, base, batch),
            max_bytes=MAX_COMMIT_REQUEST_BYTES,
        )


if __name__ == "__main__":
    main()
