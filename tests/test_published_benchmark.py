"""The production caller uses published original authority before any native build."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def helper():
    spec = importlib.util.spec_from_file_location(
        "published_benchmark", ROOT / "scripts/build_published_benchmark.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_incapable_provider_stops_before_owl_download_or_native_build(monkeypatch, tmp_path):
    module = helper()
    source = tmp_path / "facade-source"
    source.mkdir()
    (source / "pyproject.toml").write_text('[build-system]\nbuild-backend="hatchling.build"\n')
    events = []
    frozen = {"revision": "a" * 40, "files": {}}

    def pure(*args):
        events.append("pure-originals")
        return tmp_path / "original.tar.gz", tmp_path / "original.whl"

    def unavailable(*args):
        events.append("provider-capability")
        raise ValueError("Declared published provider lacks SHACL capability")

    modules = {
        "provider_coverage": SimpleNamespace(freeze_tree=lambda *args: frozen),
        "provider_validation": SimpleNamespace(require_output=lambda *args: None),
        "published_provider": SimpleNamespace(resolve=unavailable),
    }
    monkeypatch.setattr(module, "load", modules.__getitem__)
    monkeypatch.setattr(module, "pure_artifacts", pure)
    with pytest.raises(ValueError, match="lacks SHACL capability"):
        module.prepare(source, tmp_path / "proof")
    assert events == ["pure-originals", "provider-capability"]


def test_builder_receives_original_provider_and_owl_archives_without_git_guesses(tmp_path):
    module = helper()
    source = tmp_path / "facade"
    wheel = tmp_path / "facade.whl"
    wheel.write_bytes(b"original pure wheel")
    provider = {
        "source_archive": str(tmp_path / "native.tar.gz"),
        "source_sha256": "a" * 64,
        "peers": {
            "owlrl": {
                "source": str(tmp_path / "owl-source"),
                "archive": str(tmp_path / "owl.tar.gz"),
                "sha256": "b" * 64,
            }
        },
    }
    owl = {"path": str(tmp_path / "owl.whl"), "sha256": "c" * 64}
    command = module.builder_arguments(
        source, "d" * 40, wheel, provider, owl, tmp_path / "candidate"
    )
    for flag, value in {
        "--provider-archive": provider["source_archive"],
        "--provider-sha256": "a" * 64,
        "--facade-revision": "d" * 40,
        "--owlrl-archive": provider["peers"]["owlrl"]["archive"],
        "--owlrl-archive-sha256": "b" * 64,
        "--owlrl-wheel-sha256": "c" * 64,
    }.items():
        assert command[command.index(flag) + 1] == value
    assert "--provider-source" not in command and "--provider-revision" not in command
    assert "--owlrl-revision" not in command


def test_shared_workflow_prepares_published_originals_and_requires_worker_oracles():
    document = yaml.safe_load((ROOT / ".github/workflows/shared-pipeline.yml").read_text())
    job = document["jobs"]["benchmark"]
    steps = job["steps"]
    prepare = next(
        i
        for i, step in enumerate(steps)
        if "scripts/build_published_benchmark.py" in step.get("run", "")
    )
    worker = next(
        i for i, step in enumerate(steps) if "benchmarks/releases.py" in step.get("run", "")
    )
    assert prepare < worker
    assert "python -B" in steps[prepare]["run"]
    assert (
        '--candidate-wheels "$RUNNER_TEMP/pipeline-build/candidate/candidate-wheels"'
        in steps[worker]["run"]
    )
    assert "continue-on-error" not in job and "continue-on-error" not in steps[worker]
    assert document["jobs"]["publish-history"]["needs"] == "benchmark"
    uploads = [
        step for step in steps if step.get("uses", "").startswith("actions/upload-artifact@")
    ]
    assert any("candidate-build.json" in step["with"]["path"] for step in uploads)
    assert all(not step["with"]["name"].startswith("release-") for step in uploads)
