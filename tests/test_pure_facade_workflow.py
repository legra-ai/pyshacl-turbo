"""A pure facade has one archive build and portable installed-wheel acceptance."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def jobs():
    return yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())["jobs"]


def test_facade_builds_one_universal_wheel_from_original_source_archive():
    build = jobs()["wheels"]
    assert "strategy" not in build
    commands = [step.get("run", "") for step in build["steps"]]
    assert "uv build --wheel --out-dir dist source-dist/*.tar.gz" in commands
    assert not any("maturin" in command or "manylinux" in command for command in commands)
    uploads = [
        step["with"]
        for step in build["steps"]
        if step.get("uses", "").startswith("actions/upload-artifact@")
    ]
    assert uploads == [
        {"name": "release-wheel", "path": "dist/*.whl", "if-no-files-found": "error"}
    ]


def test_same_original_facade_wheel_is_required_on_every_runtime_os():
    job = jobs()["wheel-acceptance"]
    assert set(job["needs"]) == {"prepare", "wheels"}
    assert job["strategy"]["fail-fast"] is False
    assert set(job["strategy"]["matrix"]["os"]) == {
        "ubuntu-latest",
        "macos-latest",
        "windows-latest",
    }
    download = next(
        step["with"]
        for step in job["steps"]
        if step.get("uses", "").startswith("actions/download-artifact@")
    )
    assert download == {"name": "release-wheel", "path": "dist"}
    assert any(
        step.get("run") == "uv run --no-project python scripts/test_wheel.py dist"
        for step in job["steps"]
    )
    assert "wheel-acceptance" in jobs()["test"]["needs"]


def test_registry_prerequisite_uses_universal_wheel_without_native_filename_filter():
    commands = [step.get("run", "") for step in jobs()["test"]["steps"]]
    assert (
        "uv run --no-project python scripts/check_registry_pair.py dist/*-py3-none-any.whl"
        in commands
    )
