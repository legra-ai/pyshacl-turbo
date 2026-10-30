"""A release may only upload artifacts built from the revision all gates tested."""

import re
import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[1]


def test_pure_facade_preparation_and_tagging_use_the_uv_release_policy():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    prepare = next(
        step for step in workflow["jobs"]["prepare"]["steps"] if step.get("id") == "release"
    )
    tag = next(
        step
        for step in workflow["jobs"]["publish"]["steps"]
        if "/tag-tested-release@" in step.get("uses", "")
    )
    for step in [prepare, tag]:
        assert step["with"]["manifest-kind"] == "uv"
        assert step["with"]["tag-format"] == "pep440"
    assert prepare["uses"].split("@")[1] == tag["uses"].split("@")[1]


def test_release_preparation_preserves_the_minor_breaking_change_policy():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    prepare = next(
        step for step in workflow["jobs"]["prepare"]["steps"] if step.get("id") == "release"
    )
    assert prepare["with"]["breaking-change-bump"] == "minor"


def test_release_and_dependency_actions_use_one_immutable_policy_revision():
    actions = []
    for name in ("ci.yml", "dependabot-merge.yml"):
        workflow = yaml.safe_load((ROOT / ".github/workflows" / name).read_text())
        for job in workflow["jobs"].values():
            actions.extend(
                step["uses"]
                for step in job.get("steps", [])
                if step.get("uses", "").startswith("legra-ai/github-actions/.github/actions/")
            )
    assert {action.split("/")[-1].split("@")[0] for action in actions} == {
        "prepare-cargo-release",
        "tag-tested-release",
        "generate-changelog",
        "merge-tested-dependabot",
    }
    revisions = {action.split("@")[1] for action in actions}
    assert len(revisions) == 1
    assert re.fullmatch(r"[0-9a-f]{40}", revisions.pop())


def test_release_builds_only_the_original_universal_facade_wheel():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert project["build-system"]["build-backend"] == "hatchling.build"
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    wheels = workflow["jobs"]["wheels"]
    assert "strategy" not in wheels
    builds = [step["run"] for step in wheels["steps"] if "uv build" in step.get("run", "")]
    assert builds == ["uv build --wheel --out-dir dist source-dist/*.tar.gz"]
    acceptance = workflow["jobs"]["wheel-acceptance"]
    assert set(acceptance["strategy"]["matrix"]["os"]) == {
        "ubuntu-latest",
        "macos-latest",
        "windows-latest",
    }
    assert any(
        step.get("uses", "").startswith("actions/download-artifact@")
        and step["with"]["name"] == "release-wheel"
        for step in acceptance["steps"]
    )


def test_readme_links_work_on_package_index_pages():
    links = re.findall(r"\]\(([^)\s]+)\)", (ROOT / "README.md").read_text())
    assert links
    assert all(link.startswith(("https://", "#")) for link in links)


def test_release_checks_and_builds_the_prepared_revision():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    jobs = workflow["jobs"]
    assert workflow["concurrency"]["cancel-in-progress"] is False
    for name in ["verify", "sdist", "wheels", "test", "publish"]:
        job = jobs[name]
        assert "prepare" in job["needs"]
        checkouts = [
            step for step in job["steps"] if step.get("uses", "").startswith("actions/checkout@")
        ]
        assert checkouts and all(
            step["with"]["ref"] == "${{ needs.prepare.outputs.revision }}" for step in checkouts
        )
    for name in ["compatibility", "regex", "native-coverage", "shared-pipeline"]:
        assert jobs[name]["with"]["revision"] == "${{ needs.prepare.outputs.revision }}"
    assert set(jobs["test"]["needs"]) == {
        "prepare",
        "verify",
        "compatibility",
        "regex",
        "sdist",
        "wheels",
        "wheel-acceptance",
        "native-coverage",
        "shared-pipeline",
    }
    assert any(
        step.get("run") == "uv run --no-project python scripts/release_packages.py check-build"
        for step in jobs["test"]["steps"]
    )
    publish = jobs["publish"]
    assert "test" in publish["needs"]
    assert publish["environment"]["name"] == "pypi"
    assert publish["permissions"]["id-token"] == "write"
    assert "needs.prepare.outputs.release == 'true'" in publish["if"]
    steps = publish["steps"]
    upload = next(step for step in steps if step.get("run", "").startswith("uv publish "))
    assert "skip-existing" not in upload["run"]
    assert "--trusted-publishing always" in upload["run"]
    attest = next(
        i
        for i, step in enumerate(steps)
        if step.get("uses", "").startswith("astral-sh/attest-action@")
    )
    assert attest < steps.index(upload)
    assert upload["if"] == "steps.pending.outputs.missing == 'true'"
    draft = next(
        step for step in steps if step.get("uses", "").startswith("softprops/action-gh-release@")
    )
    assert draft["with"]["draft"] is True
    verify = next(
        i
        for i, step in enumerate(steps)
        if step.get("run") == "uv run --no-project python scripts/release_packages.py verify"
    )
    finalize = next(i for i, step in enumerate(steps) if "--draft=false" in step.get("run", ""))
    assert verify < finalize


def test_pure_facade_hooks_verify_python_without_a_native_toolchain():
    hook = (ROOT / ".githooks/pre-commit").read_text()
    assert "ruff check python tests benchmarks scripts" in hook
    assert "ruff format --check python tests benchmarks scripts" in hook
    assert "cargo" not in hook
    assert "fmt.sh" not in hook


@pytest.mark.parametrize(
    "workflow,job", [("native-coverage.yml", "coverage"), ("regex.yml", "regex")]
)
def test_owner_formatting_jobs_install_the_pinned_nightly(workflow, job):
    document = yaml.safe_load((ROOT / ".github/workflows" / workflow).read_text())
    assert any(
        step.get("uses") == "actions-rust-lang/setup-rust-toolchain@v2"
        and step.get("with", {}).get("toolchain") == "nightly-2026-10-16"
        and "rustfmt" in step["with"]["components"]
        for step in document["jobs"][job]["steps"]
    )


@pytest.mark.parametrize(
    "header,expected",
    [
        ("feat(api): add validation", 0),
        ("fix(rdf)!: change identity", 0),
        ("build(deps): update dependencies (#10)", 0),
        ("feat: no scope", 1),
        ("Merge branch 'main'", 1),
        ("fix(scope): trailing space ", 1),
    ],
)
def test_local_commit_policy(header, expected, tmp_path):
    import sys

    message = tmp_path / "message"
    message.write_text(header + "\n")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/commit_policy.py"), str(message)],
        capture_output=True,
        check=False,
    )
    assert (result.returncode != 0) == bool(expected)
