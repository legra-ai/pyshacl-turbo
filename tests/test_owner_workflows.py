"""Pure façade workflows delegate Rust authority without dropping native gates."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def workflow(name):
    return yaml.safe_load((ROOT / ".github/workflows" / name).read_text())


@pytest.mark.parametrize(
    "name,job,gate",
    [("native-coverage.yml", "coverage", "coverage"), ("regex.yml", "regex", "regex")],
)
def test_native_workflows_build_original_pure_wheel_and_delegate_owner(name, job, gate):
    steps = workflow(name)["jobs"][job]["steps"]
    commands = "\n".join(step.get("run", "") for step in steps)
    assert 'uv build --sdist --out-dir "$RUNNER_TEMP/facade-dist"' in commands
    assert (
        'uv build --wheel --out-dir "$RUNNER_TEMP/facade-wheel" "$RUNNER_TEMP"/facade-dist/*.tar.gz'
        in commands
    )
    assert "python -B scripts/owner_driver.py" in commands
    assert f"--gate {gate}" in commands
    assert '--facade-source "$GITHUB_WORKSPACE"' in commands
    assert '--facade-wheel "$RUNNER_TEMP"/facade-wheel/*-py3-none-any.whl' in commands
    assert "cargo doc" not in commands
    assert "scripts/native_coverage.py" not in commands
    assert "make test-regex" not in commands
    assert sum(
        "cargo-llvm-cov --version 0.9.1 --locked" in step.get("run", "") for step in steps
    ) == (gate == "coverage")


def test_coverage_artifacts_come_from_verified_provider_output():
    steps = workflow("native-coverage.yml")["jobs"]["coverage"]["steps"]
    uploads = {
        step["with"]["name"]: step
        for step in steps
        if step.get("uses", "").startswith("actions/upload-artifact@")
    }
    assert (
        uploads["native-rust-coverage"]["with"]["path"]
        == "${{ runner.temp }}/native-owner/native-coverage/"
    )
    assert (
        uploads["rust-api-documentation"]["with"]["path"]
        == "${{ runner.temp }}/native-owner/rustdoc/doc/"
    )
    assert (
        uploads["native-owner-authority"]["with"]["path"]
        == "${{ runner.temp }}/native-owner/*.json"
    )
    assert uploads["native-owner-authority"]["if"] == "always()"


def test_primary_verify_accepts_one_original_wheel_on_all_runtime_operating_systems():
    verify = workflow("ci.yml")["jobs"]["verify"]
    assert set(verify["needs"]) == {"prepare", "wheels"}
    assert {entry["os"] for entry in verify["strategy"]["matrix"]["include"]} == {
        "ubuntu-latest",
        "macos-latest",
        "windows-latest",
    }
    steps = verify["steps"]
    assert any(
        step.get("uses", "").startswith("actions/download-artifact@")
        and step["with"]["name"] == "release-wheel"
        for step in steps
    )
    commands = "\n".join(step.get("run", "") for step in steps)
    assert "python -B scripts/provider_validation.py" in commands
    assert "--facade-wheel dist/*-py3-none-any.whl" in commands
    assert "make dev" not in commands
    assert "make check" not in commands
    assert "cargo test" not in commands
    assert "test-sparql-evaluator" not in commands


def test_incapable_registry_provider_fails_before_llvm_tool_compilation():
    steps = workflow("native-coverage.yml")["jobs"]["coverage"]["steps"]
    capability = next(
        i for i, step in enumerate(steps) if "scripts/check_registry_pair.py" in step.get("run", "")
    )
    installation = next(
        i for i, step in enumerate(steps) if "cargo install cargo-llvm-cov" in step.get("run", "")
    )
    assert capability < installation


def test_pure_prepare_and_sdist_jobs_do_not_install_a_facade_rust_toolchain():
    document = workflow("ci.yml")
    for name in ("prepare", "sdist"):
        assert not any(
            "rust-toolchain" in step.get("uses", "") for step in document["jobs"][name]["steps"]
        )
    native = workflow("native-coverage.yml")["jobs"]["coverage"]
    assert any(step.get("with", {}).get("toolchain") == "1.99.1" for step in native["steps"])


def test_active_workflows_use_the_current_uv_toolchain():
    selected = []
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        document = yaml.safe_load(path.read_text())
        for job in document["jobs"].values():
            for step in job.get("steps", []):
                if step.get("uses", "").startswith("astral-sh/setup-uv@"):
                    selected.append((path.name, step))
                    assert step["uses"] == "astral-sh/setup-uv@v10.3.2"
                    assert step["with"]["version"] == "0.13.5"
    assert selected


def test_release_metadata_check_uses_current_twine():
    commands = [
        step.get("run", "")
        for job in workflow("ci.yml")["jobs"].values()
        for step in job.get("steps", [])
    ]
    assert "uv tool run --from twine==7.0.0 twine check --strict dist/*" in commands
