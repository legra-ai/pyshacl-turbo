"""One-time owner initialization of a signed artifact-only history branch.

Uses the existing Git signing identity, a temporary index, and an orphan commit.
CI then appends GitHub-signed commits without signing secrets or workflow writes.
The checked-out branch and index are never changed.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from upstream_support.process_launch import Popen

REF = "refs/heads/benchmark-results"


def git(*arguments, data=None, environment=None):
    with Popen(
        ["git", "-C", str(ROOT), *map(str, arguments)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
    ) as process:
        stdout, stderr = process.communicate(data)
        if process.returncode:
            raise RuntimeError(f"History initialization failed: {arguments}\n{stderr}")
    return stdout.strip()


def main():
    if git("ls-remote", "--heads", "origin", REF):
        raise RuntimeError("The benchmark-results branch already exists; refusing to replace it")
    before = git("write-tree")
    with tempfile.TemporaryDirectory(prefix="turbo-history-index-") as temporary:
        environment = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / "index"))
        git("read-tree", "--empty", environment=environment)
        files = {
            ".benchmark-history-format.json": json.dumps(
                {"schema": 1, "kind": "turbo-pipeline-history"}
            )
            + "\n",
            "README.md": "# Companion turbo performance history\n\nThis artifact-only branch is initialized with a verified owner signature. Successful main-branch CI appends measured Linux/macOS reports and raw evidence using GitHub-signed commits. No measurements have been published here yet.\n\nThe [initial candidate measurements](https://github.com/legra-ai/pyshacl-turbo/pull/51) are retained in the implementation PR.\n",
        }
        for name, content in files.items():
            blob = git("hash-object", "-w", "--stdin", data=content)
            git(
                "update-index",
                "--add",
                "--cacheinfo",
                f"100644,{blob},{name}",
                environment=environment,
            )
        tree = git("write-tree", environment=environment)
        commit = git(
            "commit-tree",
            "-S",
            tree,
            data="ci(history): initialize signed performance artifact branch\n",
        )
        git("verify-commit", commit)
        if git("write-tree") != before:
            raise RuntimeError("The source index changed during history initialization")
        git("push", "origin", f"{commit}:{REF}")
        print(f"Initialized {REF} at signed commit {commit}")


if __name__ == "__main__":
    main()
