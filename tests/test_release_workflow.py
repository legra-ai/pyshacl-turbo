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
    build = next(
        step for step in wheels["steps"] if "sh scripts/build_manylinux.sh" in step.get("run", "")
    )
    assert build["if"] == "runner.os == 'Linux'"
    assert "${{ matrix.container }}" in build["run"]
    assert "${{ matrix.target }}" in build["run"]
    driver = (ROOT / "scripts/build_manylinux.sh").read_text()
    inner = (ROOT / "scripts/build_manylinux_inner.sh").read_text()
    assert "--env CARGO_BUILD_WARNINGS=deny" in driver
    assert "--workdir /build" in driver
    assert '--volume "$PWD/source-build:/build"' in driver
    assert '--volume "$PWD:/io"' not in driver
    assert "uv build --wheel" in inner
    assert "--compatibility manylinux_2_28" in inner
    assert "--locked" in inner
    assert (
        tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["maturin"]["profile"]
        == "release"
    )
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
    for name in ["compatibility", "regex", "native-coverage", "shared-pipeline"]:
        assert jobs[name]["with"]["revision"] == "${{ needs.prepare.outputs.revision }}"
    assert set(jobs["test"]["needs"]) == {
        "prepare",
        "verify",
        "compatibility",
        "regex",
        "sdist",
        "wheels",
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


def test_source_archive_extraction_invalidates_stale_native_builds(tmp_path):
    import io
    import os
    import shutil
    import sys
    import tarfile

    if sys.platform == "win32":
        pytest.skip("The manylinux source-extraction path runs on Unix hosts")
    assert shutil.which("cargo") and shutil.which("tar")
    project = tmp_path / "source-build"
    (project / "src").mkdir(parents=True)
    manifest = '[package]\nname = "archive-freshness"\nversion = "0.1.0"\nedition = "2024"\n'
    old_source = 'fn main() { println!("old"); }\n'
    new_source = 'fn main() { println!("new"); }\n'
    (project / "Cargo.toml").write_text(manifest)
    (project / "src/main.rs").write_text(old_source)
    target = tmp_path / "target"
    environment = os.environ.copy()
    environment.update(CARGO_TARGET_DIR=str(target), CARGO_BUILD_BUILD_DIR=str(target / "build"))

    def build_and_read():
        subprocess.run(
            ["cargo", "build", "--offline", "--quiet"],
            cwd=project,
            env=environment,
            check=True,
            capture_output=True,
        )
        return subprocess.check_output([target / "debug/archive-freshness"], text=True).strip()

    assert build_and_read() == "old"
    archives = tmp_path / "source-dist"
    archives.mkdir()
    archive = archives / "fixture.tar.gz"
    with tarfile.open(archive, "w:gz") as output:
        for name, body in (("Cargo.toml", manifest), ("src/main.rs", new_source)):
            content = body.encode()
            entry = tarfile.TarInfo("fixture/" + name)
            entry.size = len(content)
            entry.mtime = 1
            output.addfile(entry, io.BytesIO(content))
    original_bytes = archive.read_bytes()
    # Historical archive timestamps reproduce Cargo accepting the cached old binary.
    subprocess.run(
        ["tar", "-xzf", archive, "--strip-components=1", "-C", project],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    assert (project / "src/main.rs").read_text() == new_source
    assert build_and_read() == "old"

    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    extraction = next(
        line
        for step in workflow["jobs"]["wheels"]["steps"]
        for line in step.get("run", "").splitlines()
        if line.strip().startswith("tar ")
    )
    subprocess.run(["sh", "-c", extraction], cwd=tmp_path, check=True, capture_output=True)
    assert build_and_read() == "new"
    assert archive.read_bytes() == original_bytes


def test_standalone_evaluator_ci_uses_the_actual_shared_engine_feature_profile():
    engine = tomllib.loads((ROOT / "crates/engine/Cargo.toml").read_text())
    expected = set(engine["dependencies"]["spareval"]["features"])
    makefile = (ROOT / "Makefile").read_text()
    recipes = [line for line in makefile.splitlines() if "$(SPARQL_MANIFEST)" in line]
    assert any("--features" not in recipe for recipe in recipes)
    shared = [recipe for recipe in recipes if "--features" in recipe]
    assert len(shared) == 1
    features = shared[0].split("--features ", 1)[1].strip().split(",")
    assert set(features) == expected
