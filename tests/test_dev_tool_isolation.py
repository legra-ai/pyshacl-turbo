"""Linting must not resolve an unavailable or changing native source peer."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("peer", ["missing", "invalid"])
def test_commit_hook_lints_without_resolving_the_native_peer(tmp_path, peer):
    project = tmp_path / "facade"
    project.mkdir()
    for directory in ["python", "tests", "benchmarks", "scripts", ".githooks"]:
        (project / directory).mkdir()
    shutil.copy(ROOT / ".githooks/pre-commit", project / ".githooks/pre-commit")
    shutil.copytree(
        ROOT / "tools/dev", project / "tools/dev", ignore=shutil.ignore_patterns(".venv")
    )
    shutil.copy(ROOT / "pyproject.toml", project / "pyproject.toml")
    shutil.copy(ROOT / "uv.lock", project / "uv.lock")
    if peer == "invalid":
        native = tmp_path / "rdflib-turbo"
        native.mkdir()
        (native / "pyproject.toml").write_text("This is not valid TOML")
    result = subprocess.run(
        ["sh", ".githooks/pre-commit"],
        cwd=project,
        env=dict(os.environ, UV_OFFLINE="1", UV_PROJECT_ENVIRONMENT=str(tmp_path / "env")),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
