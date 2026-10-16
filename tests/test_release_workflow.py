"""A release may only upload artifacts built from the revision all gates tested."""

import re
import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[1]


def test_linux_release_builds_use_native_manylinux_linkers_with_fatal_warnings():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    wheels = workflow["jobs"]["wheels"]
    linux = [row for row in wheels["strategy"]["matrix"]["include"] if "linux" in row["target"]]
    assert {row["container"] for row in linux} == {
        "quay.io/pypa/manylinux_2_28_x86_64:latest",
        "quay.io/pypa/manylinux_2_28_aarch64:latest",
    }
    build = next(step for step in wheels["steps"] if step.get("uses") == "PyO3/maturin-action@v1")
    assert build["if"] == "runner.os == 'Linux'"
    assert build["with"]["manylinux"] == "2_28"
    assert build["with"]["container"] == "${{ matrix.container }}"
    assert build["with"]["docker-options"] == "-e CARGO_BUILD_WARNINGS=deny"
    assert build["with"]["working-directory"] == "source-build"
    assert "--locked" in build["with"]["args"]
    assert "--release" in build["with"]["args"]
    assert "--zig" not in str(wheels)
    assert any("--strip-components=1" in step.get("run", "") for step in wheels["steps"])


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
    for name in ["compatibility", "regex", "native-coverage"]:
        assert jobs[name]["with"]["revision"] == "${{ needs.prepare.outputs.revision }}"
    assert set(jobs["test"]["needs"]) == {
        "prepare",
        "verify",
        "compatibility",
        "regex",
        "sdist",
        "wheels",
        "native-coverage",
    }
    assert any(
        step.get("run") == "python scripts/release_packages.py check-build"
        for step in jobs["test"]["steps"]
    )
    publish = jobs["publish"]
    assert "test" in publish["needs"]
    assert publish["environment"]["name"] == "pypi"
    assert publish["permissions"]["id-token"] == "write"
    assert "needs.prepare.outputs.release == 'true'" in publish["if"]
    steps = publish["steps"]
    upload = next(
        step for step in steps if step.get("uses", "").startswith("pypa/gh-action-pypi-publish@")
    )
    assert "skip-existing" not in upload.get("with", {})
    assert upload["if"] == "steps.pending.outputs.missing == 'true'"
    draft = next(
        step for step in steps if step.get("uses", "").startswith("softprops/action-gh-release@")
    )
    assert draft["with"]["draft"] is True
    verify = next(
        i
        for i, step in enumerate(steps)
        if step.get("run") == "python scripts/release_packages.py verify"
    )
    finalize = next(i for i, step in enumerate(steps) if "--draft=false" in step.get("run", ""))
    assert verify < finalize


def test_toolchains_and_hook_dependencies():
    rust = tomllib.loads((ROOT / "Cargo.toml").read_text())["workspace"]["package"]
    toolchain = tomllib.loads((ROOT / "rust-toolchain.toml").read_text())["toolchain"]
    assert toolchain["channel"] == rust["rust-version"] == "1.99.1"
    assert (ROOT / "rustfmt-toolchain").read_text().strip() == "nightly-2026-10-16"
    lock = tomllib.loads((ROOT / "Cargo.lock").read_text())
    names = {package["name"] for package in lock["package"]}
    assert "rhusky" in names
    assert "sloughi" not in names
    assert "./scripts/fmt.sh --check" in (ROOT / ".githooks/pre-commit").read_text()


@pytest.mark.parametrize("workflow,job", [("ci.yml", "verify"), ("regex.yml", "regex")])
def test_formatting_jobs_install_the_pinned_nightly(workflow, job):
    document = yaml.safe_load((ROOT / ".github/workflows" / workflow).read_text())
    assert any(
        step.get("uses") == "dtolnay/rust-toolchain@nightly"
        and step.get("with", {}).get("toolchain") == "nightly-2026-10-16"
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
