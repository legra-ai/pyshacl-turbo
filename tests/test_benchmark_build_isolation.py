"""uv extracts source archives beside its wheel output; keep Cargo isolated."""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


def builder_module():
    path = Path(__file__).resolve().parents[1] / "scripts/build_benchmark_wheels.py"
    spec = importlib.util.spec_from_file_location("benchmark_builder", path)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    return builder


def committed_source(builder, source):
    source.mkdir()
    (source / "payload.py").write_text("value = 1\n")
    (source / ".gitignore").write_text("ignored-output/\n")
    builder.run("git", "init", source)
    builder.run("git", "-C", source, "add", ".")
    builder.run(
        "git",
        "-C",
        source,
        "-c",
        "commit.gpgsign=false",
        "-c",
        "core.hooksPath=no-hooks",
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "test: record fixture",
    )


def test_dirty_candidate_fails_before_any_network_or_build(monkeypatch, tmp_path):
    import sys

    builder = builder_module()
    source = tmp_path / "source"
    committed_source(builder, source)
    (source / "payload.py").write_text("value = 2\n")
    pins = tmp_path / "pins.json"
    pins.write_text(json.dumps({"rdflib-turbo": "a" * 40, "owlrl-turbo": "b" * 40}))
    monkeypatch.setattr(builder, "ROOT", source)
    monkeypatch.setattr(
        sys, "argv", ["builder", "--sources", str(pins), "--output", str(tmp_path / "wheels")]
    )

    def unexpected(*args):
        raise AssertionError("Dirty input must fail before clone/build")

    monkeypatch.setattr(builder, "run", unexpected)
    with pytest.raises(RuntimeError, match="clean source"):
        builder.main()


def test_source_snapshots_are_committed_and_exclude_ignored_artifacts(tmp_path):
    builder = builder_module()
    source = tmp_path / "source"
    committed_source(builder, source)
    revision = builder.checked_revision(source)
    ignored = source / "ignored-output"
    ignored.mkdir()
    (ignored / "artifact.txt").write_text("must not enter a source build")
    assert builder.checked_revision(source) == revision
    checkout = tmp_path / "checkout"
    builder.checkout_source(source, revision, checkout)
    assert builder.checked_revision(checkout) == revision
    assert not (checkout / "ignored-output").exists()
    (source / "untracked.py").write_text("must fail, not be attributed to HEAD")
    with pytest.raises(RuntimeError, match="clean source"):
        builder.checked_revision(source)


def test_companion_archive_build_ignores_the_destination_cargo_workspace(tmp_path):
    path = Path(__file__).resolve().parents[1] / "scripts/build_benchmark_wheels.py"
    spec = importlib.util.spec_from_file_location("benchmark_builder", path)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    original_spawner = subprocess.Popen
    source = tmp_path / "source"
    source.mkdir()
    (source / "src").mkdir()
    (source / "pyproject.toml").write_text("""[build-system]
requires = ["maturin==1.15.0"]
build-backend = "maturin"
[project]
name = "isolated-benchmark-fixture"
version = "0.1.0"
[tool.maturin]
bindings = "bin"
""")
    (source / "Cargo.toml").write_text("""[package]
name = "isolated-benchmark-fixture"
version = "0.1.0"
edition = "2024"
""")
    (source / "src/main.rs").write_text('fn main() { println!("isolated"); }\n')
    parent = tmp_path / "unrelated-workspace"
    parent.mkdir()
    (parent / "Cargo.toml").write_text("[workspace]\nmembers = []\n")
    output = parent / "pipeline-wheels"
    output.mkdir()
    archives = tmp_path / "archives"
    builder.run("uv", "build", "--sdist", "--out-dir", archives, source)
    archive = next(archives.glob("*.tar.gz"))
    wheel = builder.build_archive(archive, output, tmp_path / "isolated-output")
    assert wheel.is_file() and wheel.parent == output
    assert not list(parent.glob("pipeline-wheels/.tmp*"))
    assert subprocess.Popen is original_spawner


def test_candidate_rejects_stale_embedded_engine_before_build(tmp_path):
    builder = builder_module()
    canonical = tmp_path / "canonical"
    committed_source(builder, canonical)
    stale = builder.checked_revision(canonical)
    implementation = canonical / "crates/engine/src"
    implementation.mkdir(parents=True)
    (implementation / "lib.rs").write_text("pub trait GraphRead {}\n")
    builder.run("git", "-C", canonical, "add", ".")
    builder.run(
        "git",
        "-C",
        canonical,
        "-c",
        "commit.gpgsign=false",
        "-c",
        "core.hooksPath=no-hooks",
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "test: add canonical reader",
    )
    current = builder.checked_revision(canonical)
    runtime = tmp_path / "runtime"
    runtime.mkdir()

    def declare(revision):
        (runtime / "Cargo.toml").write_text(
            "[dependencies]\npyshacl-turbo-engine = {git = "
            '"https://github.com/legra-ai/pyshacl-turbo", rev = "' + revision + '"}\n'
        )

    declare(stale)
    with pytest.raises(RuntimeError, match="canonical SHACL engine"):
        builder.ensure_shared_engine(canonical, runtime)
    declare(current)
    builder.ensure_shared_engine(canonical, runtime)
