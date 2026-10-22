"""Build-script hook installation belongs only to the explicitly opted-in checkout."""

import os
import subprocess
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def checkout(path):
    path.mkdir()
    subprocess.run(["git", "init", "--quiet", str(path)], check=True)
    return path


def build_probe(source, *, configured_root=None, skip_env=None):
    crate = source / "crates" / "engine"
    crate.mkdir(parents=True)
    (crate / "src").mkdir()
    (crate / "src" / "lib.rs").write_text("")
    version = tomllib.loads((ROOT / "crates/engine/Cargo.toml").read_text())["build-dependencies"][
        "rhusky"
    ]
    (crate / "Cargo.toml").write_text(
        '[package]\nname = "hook-owner-probe"\nversion = "0.0.0"\nedition = "2024"\n'
        f'[build-dependencies]\nrhusky = "{version}"\n'
    )
    (crate / "build.rs").write_bytes((ROOT / "crates/engine/build.rs").read_bytes())
    (crate / "Cargo.lock").write_bytes((ROOT / "Cargo.lock").read_bytes())
    run_probe(source, configured_root=configured_root, skip_env=skip_env)


def run_probe(source, *, configured_root=None, skip_env=None):
    crate = source / "crates" / "engine"
    environment = os.environ.copy()
    for key in ("CI", "GITHUB_ACTIONS", "RHUSKY_REPOSITORY_ROOT"):
        environment.pop(key, None)
    if configured_root is not None:
        environment["RHUSKY_REPOSITORY_ROOT"] = str(configured_root)
    if skip_env is not None:
        environment[skip_env] = "1"
    # bounded: one shared target for this fixed three-case build-script fixture.
    environment["CARGO_TARGET_DIR"] = str(ROOT / "target" / "hook-owner-probe")
    process = subprocess.run(
        ["cargo", "build", "--quiet", "--manifest-path", str(crate / "Cargo.toml")],
        cwd=source,
        env=environment,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=180,
    )
    assert process.returncode == 0, process.stdout


def test_nested_engine_installs_only_into_configured_checkout(tmp_path):
    source = checkout(tmp_path / "checkout")
    hooks = source / ".githooks"
    hooks.mkdir()
    marker = hooks / "pre-commit"
    marker.write_text("existing repository hook\n")
    build_probe(source, configured_root=source)
    configured = subprocess.check_output(
        ["git", "-C", str(source), "config", "--local", "--get", "core.hooksPath"],
        text=True,
    ).strip()
    assert configured == ".githooks"
    assert marker.read_text() == "existing repository hook\n"


def test_dependency_without_checkout_opt_in_does_not_install_hooks(tmp_path):
    dependency = checkout(tmp_path / "dependency")
    before = (dependency / ".git" / "config").read_bytes()
    build_probe(dependency)
    assert (dependency / ".git" / "config").read_bytes() == before
    assert not (dependency / ".githooks").exists()


def test_inherited_caller_opt_in_cannot_install_dependency_hooks(tmp_path):
    caller = checkout(tmp_path / "caller")
    dependency = checkout(tmp_path / "dependency")
    before = [(path / ".git" / "config").read_bytes() for path in (caller, dependency)]
    build_probe(dependency, configured_root=caller)
    assert [(path / ".git" / "config").read_bytes() for path in (caller, dependency)] == before
    assert not (caller / ".githooks").exists()
    assert not (dependency / ".githooks").exists()


def test_activating_checkout_opt_in_rebuilds_the_installer(tmp_path):
    source = checkout(tmp_path / "checkout")
    build_probe(source)
    assert not (source / ".githooks").exists()
    run_probe(source, configured_root=source)
    assert (source / ".githooks" / "pre-commit").is_file()


def test_empty_configured_root_remains_a_hard_error(tmp_path):
    source = checkout(tmp_path / "checkout")
    with pytest.raises(AssertionError, match="Checkout root is empty"):
        build_probe(source, configured_root="")


@pytest.mark.parametrize("skip_env", ["CI", "GITHUB_ACTIONS"])
def test_leaving_ci_rebuilds_the_checkout_installer(tmp_path, skip_env):
    source = checkout(tmp_path / "checkout")
    build_probe(source, configured_root=source, skip_env=skip_env)
    assert not (source / ".githooks").exists()
    run_probe(source, configured_root=source)
    assert (source / ".githooks" / "pre-commit").is_file()
