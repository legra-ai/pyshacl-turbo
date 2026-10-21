"""Publication requires declared registry companions, independently of Git dev sources."""

import importlib.util
import subprocess
import zipfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_gate():
    path = ROOT / "scripts/check_registry_pair.py"
    assert path.is_file(), "the publisher needs a registry-only installed-wheel gate"
    spec = importlib.util.spec_from_file_location("check_registry_pair", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wheel(tmp_path, requirement='rdflib-turbo==0.2.0a7; extra == "test"'):
    archive = tmp_path / "pyshacl_turbo-0.5.1-py3-none-any.whl"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr(
            "pyshacl_turbo-0.5.1.dist-info/METADATA",
            "Metadata-Version: 2.4\nName: pyshacl-turbo\nVersion: 0.5.1\n"
            f"Provides-Extra: test\nRequires-Dist: {requirement}\n",
        )
    return archive


def fake_uv(monkeypatch, gate, source, *, fail=False):
    commands = []

    def run(command, **kwargs):
        command = list(map(str, command))
        commands.append((command, kwargs["env"]))
        if "add" in command:
            if fail:
                return subprocess.CompletedProcess(command, 1, "", "No matching distribution")
            project = Path(command[command.index("--directory") + 1])
            project.mkdir(exist_ok=True)
            (project / "uv.lock").write_text(
                'version = 1\n[[package]]\nname = "rdflib-turbo"\n'
                f"source = {source}\n"
            )
        return subprocess.CompletedProcess(command, 0, "pair compatible", "")

    monkeypatch.setattr(gate.subprocess, "run", run)
    return commands


def test_fresh_registry_environment_cannot_inherit_dev_sources(tmp_path, monkeypatch):
    gate = load_gate()
    artifact = wheel(tmp_path)
    monkeypatch.setenv("UV_INDEX", "https://untrusted.invalid/simple")
    monkeypatch.setenv("UV_PROJECT_ENVIRONMENT", "/unrelated/environment")
    monkeypatch.setenv("PYTHONPATH", "/unrelated/source")
    monkeypatch.setenv("PIP_INDEX_URL", "https://untrusted.invalid/simple")
    commands = fake_uv(monkeypatch, gate, '{ registry = "https://pypi.org/simple" }')
    gate.verify(artifact)
    add, env = next((command, env) for command, env in commands if "add" in command)
    assert str(artifact.resolve()) in add
    assert "--no-sync" in add and add[add.index("--extra") + 1] == "test"
    assert add[add.index("--default-index") + 1] == "https://pypi.org/simple"
    assert "UV_INDEX" not in env and "UV_PROJECT_ENVIRONMENT" not in env
    assert "PYTHONPATH" not in env and "PIP_INDEX_URL" not in env
    assert env["UV_NO_BUILD"] == "1"
    assert any("sync" in command and "--locked" in command for command, _ in commands)
    assert commands[-1][0][-2:] == ["-c", gate.PROBE]
    assert "-I" in commands[-1][0]


@pytest.mark.parametrize(
    "source",
    [
        '{ git = "https://example.invalid/runtime#123" }',
        '{ path = "/candidate/runtime.whl" }',
        '{ registry = "https://mirror.invalid/simple" }',
    ],
)
def test_non_registry_provider_fails_before_import(tmp_path, monkeypatch, source):
    gate = load_gate()
    commands = fake_uv(monkeypatch, gate, source)
    with pytest.raises(ValueError, match="PyPI registry"):
        gate.verify(wheel(tmp_path))
    assert not any("-c" in command for command, _ in commands)


def test_unavailable_declared_version_aborts_before_probe(tmp_path, monkeypatch):
    gate = load_gate()
    commands = fake_uv(monkeypatch, gate, '{}', fail=True)
    with pytest.raises(RuntimeError, match="No matching distribution"):
        gate.verify(wheel(tmp_path))
    assert not any("sync" in command or "-c" in command for command, _ in commands)


def test_direct_url_runtime_requirement_is_rejected(tmp_path):
    gate = load_gate()
    with pytest.raises(ValueError, match="registry requirement"):
        gate.verify(wheel(tmp_path, 'rdflib-turbo @ https://example.invalid/candidate.whl'))


def test_publication_depends_on_registry_pair_before_any_tagging():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    jobs = workflow["jobs"]
    assert "test" in jobs["publish"]["needs"]
    steps = jobs["test"]["steps"]
    guard = next(step for step in steps if "check_registry_pair.py" in step.get("run", ""))
    inventory = next(step for step in steps if "check-build" in step.get("run", ""))
    assert steps.index(inventory) < steps.index(guard)
    assert "refs/heads/main" in guard["if"] and "release" in guard["if"]
    assert "continue-on-error" not in guard
    assert "manylinux" in guard["run"] and "x86_64" in guard["run"]


@pytest.mark.parametrize("canonical,provider", [(None, None), ("candidate", "older")])
def test_installed_probe_rejects_missing_or_different_fingerprints(monkeypatch, canonical, provider):
    import sys
    from types import SimpleNamespace

    gate = load_gate()
    monkeypatch.setitem(
        sys.modules, "pyshacl_turbo",
        SimpleNamespace(_native=SimpleNamespace(SHACL_ENGINE_FINGERPRINT=canonical)),
    )
    monkeypatch.setitem(
        sys.modules, "rdflib_turbo",
        SimpleNamespace(_native=SimpleNamespace(SHACL_ENGINE_FINGERPRINT=provider)),
    )
    with pytest.raises(RuntimeError, match="different SHACL engine"):
        exec(gate.PROBE, {})
