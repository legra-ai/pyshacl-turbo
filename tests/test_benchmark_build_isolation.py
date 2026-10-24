"""uv extracts source archives beside its wheel output; keep Cargo isolated."""

import hashlib
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


def test_release_builder_rejects_profile_overrides_before_any_native_work(monkeypatch, tmp_path):
    module = builder_module()
    monkeypatch.setenv("CARGO_PROFILE_RELEASE_OPT_LEVEL", "0")
    with pytest.raises(ValueError, match="profile override"):
        module.build_environment(tmp_path)


def test_release_builder_rejects_git_to_archive_equivalence_before_build(monkeypatch, tmp_path):
    module = builder_module()
    monkeypatch.setattr(
        module.sys,
        "argv",
        [
            "builder",
            "--provider-source",
            str(tmp_path),
            "--provider-revision",
            "a" * 40,
            "--facade-source",
            str(tmp_path),
            "--facade-revision",
            "b" * 40,
            "--facade-wheel",
            str(tmp_path / "facade.whl"),
            "--facade-wheel-sha256",
            "c" * 64,
            "--owlrl-source",
            str(tmp_path),
            "--owlrl-revision",
            "d" * 40,
            "--owlrl-wheel",
            str(tmp_path / "owl.whl"),
            "--owlrl-wheel-sha256",
            "e" * 64,
            "--output",
            str(tmp_path / "output"),
        ],
    )
    with pytest.raises(ValueError, match="Git.*archive.*unsupported"):
        module.main()
    assert not (tmp_path / "output").exists()


def test_pinned_uv_accepts_its_actual_distribution_build_metadata():
    module = builder_module()
    module.require_uv_version("uv 0.13.1 (Homebrew 2026-10-14 aarch64-apple-darwin)")
    module.require_uv_version("uv 0.13.1")
    for wrong in ("uv 0.4.27", "uv 0.13.10", "other 0.13.1", "uv 0.13.1-dev"):
        with pytest.raises(ValueError, match="pinned uv"):
            module.require_uv_version(wrong)


@pytest.mark.parametrize(
    "name",
    [
        "CARGO_BUILD_RUSTFLAGS",
        "CARGO_TARGET_AARCH64_APPLE_DARWIN_RUSTFLAGS",
        "CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_RUSTFLAGS",
    ],
)
def test_release_builder_rejects_cargo_build_and_target_flag_overrides(monkeypatch, tmp_path, name):
    module = builder_module()
    (tmp_path / "rust-toolchain.toml").write_text('[toolchain]\nchannel="1.99.1"\n')
    monkeypatch.setenv(name, "-C opt-level=0")
    with pytest.raises(ValueError, match="profile override"):
        module.build_environment(tmp_path)


def test_release_builder_preserves_configured_compiler_cache_wrappers(monkeypatch, tmp_path):
    module = builder_module()
    (tmp_path / "rust-toolchain.toml").write_text('[toolchain]\nchannel="1.99.1"\n')
    monkeypatch.setenv("RUSTC_WRAPPER", "/configured/sccache")
    monkeypatch.setenv("CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER", "/configured/workspace-wrapper")
    env = module.build_environment(tmp_path)
    assert env["RUSTC_WRAPPER"] == "/configured/sccache"
    assert env["CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER"] == "/configured/workspace-wrapper"


def test_peer_wheels_are_retained_byte_identical_without_overwriting_originals(tmp_path):
    module = builder_module()
    original = tmp_path / "original-pure.whl"
    original.write_bytes(b"original wheel bytes")
    output = tmp_path / "candidate-wheels"
    output.mkdir()
    digest = hashlib.sha256(original.read_bytes()).hexdigest()
    retained = module.copy_original_wheel(original, output, digest)
    assert retained.name == original.name
    assert retained.read_bytes() == original.read_bytes() == b"original wheel bytes"
    with pytest.raises(FileExistsError):
        module.copy_original_wheel(original, output, digest)
    with pytest.raises(ValueError, match="original.*SHA-256"):
        module.copy_original_wheel(original, output, "0" * 64)


def test_worker_source_manifest_is_emitted_only_for_verified_release_inputs(tmp_path):
    module = builder_module()
    source_file = tmp_path / "sources.json"
    receipt_file = tmp_path / "candidate-build.json"
    receipt = {"status": "prepared", "performance_eligible": False}
    receipt_file.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="verified RELEASE"):
        module.write_worker_sources(receipt, receipt_file, source_file)
    assert not source_file.exists()
    receipt.update(
        status="verified",
        performance_eligible=True,
        build_authority={"archive_sha256": "a" * 64},
        source_identity={"engine_fingerprint": "b" * 64},
        peers={
            "facade": {"source": {"kind": "git", "revision": "c" * 40}},
            "owlrl": {"source": {"kind": "original-sdist", "sha256": "d" * 64}},
        },
        harness_source={"revision": "e" * 40},
        installed_candidate={"original_wheels": {"rdflib-turbo": {"sha256": "f" * 64}}},
    )
    receipt_file.write_text(json.dumps(receipt))
    module.write_worker_sources(receipt, receipt_file, source_file)
    manifest = json.loads(source_file.read_text())
    assert manifest["rdflib-turbo"] == {
        "kind": "original-sdist",
        "sha256": "a" * 64,
        "engine_fingerprint": "b" * 64,
    }
    assert manifest["owlrl-turbo"] == {"kind": "original-sdist", "sha256": "d" * 64}
    assert manifest["reference_equality_gate"] == "benchmarks/releases.py"
    assert manifest["build_receipt_sha256"] == hashlib.sha256(receipt_file.read_bytes()).hexdigest()


def test_release_builder_preserves_the_real_setup_action_dev_profile_environment(
    monkeypatch, tmp_path
):
    module = builder_module()
    (tmp_path / "rust-toolchain.toml").write_text('[toolchain]\nchannel="1.99.1"\n')
    monkeypatch.setenv("CARGO_PROFILE_DEV_DEBUG", "0")
    monkeypatch.setenv("CARGO_INCREMENTAL", "0")
    monkeypatch.setenv("CARGO_BUILD_WARNINGS", "deny")
    env = module.build_environment(tmp_path)
    assert env["CARGO_PROFILE_DEV_DEBUG"] == "0"
    assert env["CARGO_INCREMENTAL"] == "0"
    assert env["CARGO_BUILD_WARNINGS"] == "deny"
