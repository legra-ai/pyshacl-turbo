"""Artifact keys and links use portable separators, not host path spelling."""

import json
from pathlib import Path, PureWindowsPath

from test_benchmark import benchmark_module
from test_benchmark_history import artifacts
from test_benchmark_history import module as history_module
from test_release_benchmark import module as releases_module


def windows_relative_paths(patch):
    original = Path.relative_to

    def relative(path, *args, **kwargs):
        return PureWindowsPath(original(path, *args, **kwargs).as_posix())

    patch.setattr(Path, "relative_to", relative)


def test_release_harness_hash_keys_are_portable_on_windows(monkeypatch):
    module = releases_module()
    with monkeypatch.context() as patch:
        windows_relative_paths(patch)
        hashes = module.harness_hashes()
    assert "benchmarks/releases.py" in hashes
    assert all("\\" not in name for name in hashes)


def test_matrix_source_hash_keys_are_portable_on_windows(tmp_path, monkeypatch):
    module = benchmark_module()
    output = tmp_path / "matrix.json"
    monkeypatch.setattr(
        "sys.argv",
        ["matrix.py", "--quick", "--kinds", "core", "--repeats", "1", "--output", str(output)],
    )
    with monkeypatch.context() as patch:
        windows_relative_paths(patch)
        module.main()
    hashes = json.loads(output.read_text())["source_sha256"]
    assert "python/pyshacl_turbo/_native.py" in hashes
    assert all("\\" not in name for name in hashes)


def test_history_links_use_url_paths_with_windows_relative_paths(tmp_path, monkeypatch):
    module = history_module()
    source, destination = tmp_path / "input", tmp_path / "history"
    artifacts(source)
    monkeypatch.setattr(module, "Path", PureWindowsPath)
    module.stage_reports(source, destination, "123-1", "https://github.com/example/run/123")
    rows = json.loads((destination / "history.json").read_text())
    assert len(rows) == 2
    for row in rows:
        assert row["report"] == f"runs/123-1/{row['platform']}/releases.md"
        assert row["raw"] == f"runs/123-1/{row['platform']}/releases.json.gz"
