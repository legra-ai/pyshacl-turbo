"""uv extracts source archives beside its wheel output; keep Cargo isolated."""

import importlib.util
from pathlib import Path


def test_companion_archive_build_ignores_the_destination_cargo_workspace(tmp_path):
    path = Path(__file__).resolve().parents[1] / "scripts/build_benchmark_wheels.py"
    spec = importlib.util.spec_from_file_location("benchmark_builder", path)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    builder.install()
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
