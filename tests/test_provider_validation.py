"""Pure facade checks exercise original wheels and the actual published owner."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def helper():
    path = Path(__file__).resolve().parents[1] / "scripts/provider_validation.py"
    spec = importlib.util.spec_from_file_location("provider_validation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validation_output_cannot_change_frozen_source(tmp_path):
    with pytest.raises(ValueError, match="outside frozen facade"):
        helper().require_output(tmp_path / "source", tmp_path / "source/output")


def test_installed_checks_require_actual_registry_native_and_fa_payload_receipts(tmp_path):
    source, wheel, project = [tmp_path / name for name in ("owner", "facade.whl", "project")]
    code = helper().installed_probe(source, wheel, project)
    assert "verify_loaded_facade" in code
    assert "direct_url.json" in code
    assert "SHARED_SHACL_PROTOCOL" in code
    assert "forbid_conversion" in code
    assert "RECEIPT_PROBE" not in code


def test_full_installed_tests_use_isolated_uv_and_preserve_coverage_gate(tmp_path):
    source, project, output = [tmp_path / name for name in ("source", "project", "output")]
    command = helper().test_command(source, project, output, coverage=True)
    assert command[:9] == [
        "uv",
        "run",
        "--project",
        str(project),
        "--locked",
        "--no-sync",
        "python",
        "-I",
        "-m",
    ]
    assert command[9] == "pytest"
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
    result = helper().run(
        ["uv", "run", "--no-project", "--python", sys.executable, "python", "-c", code],
        env=helper().environment(),
        capture=True,
    )
    assert result.strip() == "True"
    assert {path.name for path in tmp_path.iterdir()} == {"original_source.py"}
