"""Pure facade checks exercise original wheels and the actual published owner."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


def helper():
    path = Path(__file__).resolve().parents[1] / "scripts/provider_validation.py"
    spec = importlib.util.spec_from_file_location("provider_validation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_captured_failure_reports_both_streams_and_preserves_the_exception(monkeypatch, capsys):
    module = helper()
    failure = subprocess.CalledProcessError(
        7, ["original-tool"], output="captured output\n", stderr="actual failure cause\n"
    )

    def fail(*args, **kwargs):
        raise failure

    monkeypatch.setattr(module.subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError) as actual:
        module.run(["original-tool"], capture=True)
    assert actual.value is failure
    streams = capsys.readouterr()
    assert streams.out == "captured output\n"
    assert streams.err == "actual failure cause\n"


def test_three_product_probe_uses_the_original_expand_only_owl_api(tmp_path):
    scripts = tmp_path / "owner/scripts"
    scripts.mkdir(parents=True)
    # Unit verifier stubs isolate the API call; original-wheel authority is
    # independently exercised by the complete published-provider gate.
    for name in ("pure_companion.py", "yaml_test_inputs.py"):
        (scripts / name).write_text(
            "def verify_loaded(wheel, environment):\n    return {'unit_verifier': True}\n"
        )
    code = helper().owl_probe(
        tmp_path / "owner", tmp_path / "owl.whl", tmp_path / "project", tmp_path / "yaml.whl"
    )
    script = tmp_path / "probe.py"
    script.write_text(
        "import owlrl_turbo\n"
        "for name in ('DeductiveClosure', 'RDFS_OWLRL_Semantics'):\n"
        "    if hasattr(owlrl_turbo, name): delattr(owlrl_turbo, name)\n" + code
    )
    spec = importlib.util.spec_from_file_location(
        "probe_launcher", Path(__file__).parent / "upstream_support/process_launch.py"
    )
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    process_type = launcher.Popen if sys.platform == "darwin" else subprocess.Popen
    with process_type(
        [sys.executable, "-I", "-B", str(script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        stdout, stderr = process.communicate(timeout=20)
        assert process.returncode == 0, stderr
    record = json.loads(stdout)
    assert record["pipeline"] == {
        "canonical_dataset": True,
        "inferred_type": True,
        "conforms": True,
        "same_native_owner": True,
    }


def test_validation_output_cannot_change_frozen_source(tmp_path):
    with pytest.raises(ValueError, match="outside frozen facade"):
        helper().require_output(tmp_path / "source", tmp_path / "source/output")


def test_installed_checks_require_actual_registry_native_and_fa_payload_receipts(
    tmp_path, monkeypatch
):
    source, wheel, project = [tmp_path / name for name in ("owner", "facade.whl", "project")]
    code = helper().installed_probe(source, wheel, project)
    assert "verify_loaded_facade" in code
    assert "direct_url.json" in code
    assert "SHARED_SHACL_PROTOCOL" in code
    assert "forbid_conversion" in code
    assert "RECEIPT_PROBE" not in code
    module = helper()
    commands = []
    monkeypatch.setattr(
        module, "run", lambda command, **kwargs: commands.append(command) or "{}\n{}\n"
    )
    assert module.installed_receipts(source, wheel, project, {}) == [{}, {}]
    index = commands[0].index("python")
    assert commands[0][index : index + 4] == ["python", "-I", "-B", "-c"]


def test_full_installed_tests_use_isolated_uv_and_preserve_coverage_gate(tmp_path):
    source, project, output = [tmp_path / name for name in ("source", "project", "output")]
    command = helper().test_command(source, project, output, coverage=True)
    assert command[:10] == [
        "uv",
        "run",
        "--project",
        str(project),
        "--locked",
        "--no-sync",
        "python",
        "-I",
        "-B",
        "-m",
    ]
    assert command[10] == "pytest"
    assert str(source / "tests") in command
    assert "--cov-fail-under=100" in command
    assert "--cov-branch" in command
    assert "--import-mode=importlib" in command


def test_current_acceptance_receipt_must_bind_every_source_byte():
    module = helper()
    original = {"revision": "a" * 40, "files": {"python/pyshacl_turbo/__init__.py": "b" * 64}}
    actual = {"revision": "a" * 40, "source_sha256": dict(original["files"])}
    module.verify_acceptance_binding(original, actual)
    actual["source_sha256"]["python/pyshacl_turbo/__init__.py"] = "c" * 64
    with pytest.raises(ValueError, match="current acceptance source"):
        module.verify_acceptance_binding(original, actual)


def test_post_test_runtime_payload_drift_is_a_hard_error(tmp_path, monkeypatch):
    module = helper()
    expected_native = {"payload": {"rdflib_turbo/_native.so": "a" * 64}}
    changed_native = {"payload": {"rdflib_turbo/_native.so": "b" * 64}}
    facade = {"package_payload": "unchanged"}
    context = {
        "owner": tmp_path / "owner",
        "wheel": tmp_path / "facade.whl",
        "project": tmp_path / "project",
        "environment": {},
        "receipt": {"installed_provider": expected_native, "installed_facade": facade},
    }
    monkeypatch.setattr(
        module,
        "run",
        lambda *args, **kwargs: json.dumps(changed_native) + "\n" + json.dumps(facade),
    )
    with pytest.raises(ValueError, match="Installed runtime payload changed"):
        module.verify_runtime(context)


def test_validation_subprocesses_never_generate_files_in_original_owner_sources():
    assert helper().environment()["PYTHONDONTWRITEBYTECODE"] == "1"


def test_actual_uv_child_preserves_bytecode_disabled_source_inventory(tmp_path):
    source = tmp_path / "original_source.py"
    source.write_text("VALUE = 'original'\n")
    code = (
        "import importlib.util,sys; "
        f"spec=importlib.util.spec_from_file_location('original_source',{str(source)!r}); "
        "module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); "
        "assert module.VALUE == 'original'; print(sys.dont_write_bytecode)"
    )
    module = helper()
    generated = module.test_command(tmp_path, tmp_path, tmp_path, coverage=False)
    flags = generated[generated.index("python") + 1 : generated.index("-m")]
    result = module.run(
        ["uv", "run", "--no-project", "--python", sys.executable, "python", *flags, "-c", code],
        env=module.environment(),
        capture=True,
    )
    assert result.strip() == "True"
    assert {path.name for path in tmp_path.iterdir()} == {"original_source.py"}


def test_explicit_original_owl_and_yaml_wheels_precede_one_no_build_sync(tmp_path, monkeypatch):
    module = helper()
    project = tmp_path / "project"
    project.mkdir()
    (project / "uv.lock").write_text(
        '[[package]]\nname="rdflib-turbo"\nversion="0.2.0a19"\n'
        'source={registry="https://pypi.org/simple"}\n'
    )
    calls = []
    monkeypatch.setattr(module, "run", lambda command, **kwargs: calls.append((command, kwargs)))
    owl, yaml = tmp_path / "original-owl.whl", tmp_path / "original-yaml.whl"
    module.install_test_peers(project, owl, yaml, {"provider_version": "0.2.0a19"}, {"FROZEN": "1"})
    assert calls == [
        (["uv", "add", "--project", project, "--no-sync", owl, yaml], {"env": {"FROZEN": "1"}}),
        (["uv", "sync", "--project", project, "--locked", "--no-build"], {"env": {"FROZEN": "1"}}),
    ]


def test_yaml_loaded_probe_executes_only_the_verified_owner_helper(tmp_path, monkeypatch):
    module = helper()
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return json.dumps({"opaque": "verified-yaml-proof"})

    monkeypatch.setattr(module, "run", run)
    owner, wheel, project = tmp_path / "owner", tmp_path / "yaml.whl", tmp_path / "project"
    assert module.installed_yaml_receipt(owner, wheel, project, {}) == {
        "opaque": "verified-yaml-proof"
    }
    assert calls[0] == [
        "uv",
        "run",
        "--project",
        project,
        "--locked",
        "--no-sync",
        "python",
        "-I",
        "-B",
        owner / "scripts/yaml_test_inputs.py",
        "--wheel",
        wheel,
        "--environment",
        project / ".venv",
    ]


@pytest.mark.parametrize("change", [False, True])
def test_original_yaml_inputs_are_rechecked_even_after_a_failed_consumer(
    tmp_path, monkeypatch, change
):
    from types import SimpleNamespace

    module = helper()
    authority = tmp_path / "yaml-inputs.json"
    authority.write_text('{"original": true}')
    dependency = {"authority": str(authority), "record": {"original": True}}
    calls = []

    def verify(owner, selected):
        calls.append(selected)
        return {"record": selected["record"], "wheel": tmp_path / "original.whl"}

    monkeypatch.setattr(
        module, "load", lambda name: SimpleNamespace(verify_yaml_test_dependency=verify)
    )
    failure = RuntimeError("original consumer failure")
    with (
        pytest.raises(
            ValueError if change else RuntimeError, match="YAML|consumer failure"
        ) as actual,
        module.frozen_yaml_inputs(tmp_path, dependency) as (verified, original_sha),
    ):
        assert verified["wheel"] == tmp_path / "original.whl"
        assert len(original_sha) == 64
        if change:
            authority.write_text('{"original": true}\n')
        raise failure
    if not change:
        assert actual.value is failure
    assert calls == [dependency, dependency]
