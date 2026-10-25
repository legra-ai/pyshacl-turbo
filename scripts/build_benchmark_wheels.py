"""Build a RELEASE candidate from an explicit original native source archive."""

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from upstream_support.process_launch import Popen


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*arguments, environment=None):
    with Popen(list(map(str, arguments)), env=environment) as process:
        code = process.wait()
    if code:
        raise subprocess.CalledProcessError(code, arguments)


def output(*arguments):
    with Popen(list(map(str, arguments)), stdout=subprocess.PIPE, text=True) as process:
        value, _ = process.communicate()
        code = process.returncode
    if code:
        raise subprocess.CalledProcessError(code, arguments)
    return value.strip()


def build_archive(archive, output, isolated_output, *, environment=None, python="3.13"):
    """uv unpacks beside --out-dir, so keep native sources outside callers' Cargo workspaces."""
    run(*archive_command(archive, isolated_output, python), environment=environment)
    wheels = list(isolated_output.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected exactly one built wheel: {archive}")
    destination = output / wheels[0].name
    shutil.copy2(wheels[0], destination)
    if load("provider_validation").digest(destination) != load("provider_validation").digest(
        wheels[0]
    ):
        raise ValueError("Copied original candidate wheel bytes changed")
    return destination


def archive_command(archive, isolated_output, python):
    return ["uv", "build", "--wheel", "--python", python, "--out-dir", isolated_output, archive]


def copy_original_wheel(wheel, output, sha256):
    if load("provider_validation").digest(wheel) != sha256:
        raise ValueError("Supplied original wheel SHA-256 mismatch")
    destination = output / wheel.name
    if destination.exists():
        raise FileExistsError(destination)
    shutil.copy2(wheel, destination)
    if load("provider_validation").digest(destination) != sha256:
        raise ValueError("Retained original wheel SHA-256 mismatch")
    return destination


def build_environment(owner):
    forbidden = [
        name
        for name in os.environ
        if name in {"RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "CARGO_BUILD_RUSTFLAGS"}
        or (name.startswith("CARGO_TARGET_") and name.endswith("_RUSTFLAGS"))
        or name.startswith(("MATURIN_", "CARGO_PROFILE_RELEASE_", "UV_CONFIG_SETTING"))
    ]
    if forbidden:
        raise ValueError(
            "Native timing builds reject external build/profile override inputs: "
            + ", ".join(sorted(forbidden))
        )
    env = load("provider_validation").environment()
    del env["UV_NO_BUILD"]
    env.update(RUSTUP_TOOLCHAIN=load("owner_gates").compiler(owner), PYO3_PYTHON=sys.executable)
    return env


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--provider-archive", type=Path)
    result.add_argument("--provider-sha256")
    result.add_argument(
        "--provider-source", type=Path, help="Unsupported Git-to-build requests fail explicitly"
    )
    result.add_argument("--provider-revision")
    for prefix in ("facade", "owlrl"):
        result.add_argument("--" + prefix + "-source", type=Path, required=True)
        result.add_argument("--" + prefix + "-revision", required=prefix == "facade")
        result.add_argument("--" + prefix + "-wheel", type=Path, required=True)
        result.add_argument("--" + prefix + "-wheel-sha256", required=True)
    result.add_argument("--owlrl-archive", type=Path)
    result.add_argument("--owlrl-archive-sha256")
    result.add_argument("--output", type=Path, required=True)
    return result


def require_uv_version(version):
    if version.split()[:2] != ["uv", "0.13.5"]:
        raise ValueError("Candidate builds require the pinned uv 0.13.5")


def write_worker_sources(receipt, receipt_file, source_file):
    if receipt["status"] != "verified" or receipt["performance_eligible"] is not True:
        raise ValueError("Worker source manifests require verified RELEASE measurement inputs")
    peers = receipt["peers"]
    manifest = {
        "rdflib-turbo": {
            "kind": "original-sdist",
            "sha256": receipt["build_authority"]["archive_sha256"],
            "engine_fingerprint": receipt["source_identity"]["engine_fingerprint"],
        },
        "pyshacl-turbo": peers["facade"]["source"],
        "owlrl-turbo": peers["owlrl"]["source"],
        "harness_revision": receipt["harness_source"]["revision"],
        "original_wheels": receipt["installed_candidate"]["original_wheels"],
        "build_receipt_sha256": load("provider_validation").digest(receipt_file),
        "reference_equality_gate": "benchmarks/releases.py",
    }
    source_file.write_text(json.dumps(manifest, indent=2) + "\n")


def main():
    args = parser().parse_args()
    authority = load("benchmark_owner")
    authority.require_build_authority(args)
    if not sys.dont_write_bytecode:
        raise ValueError("Original-archive candidate builds require python -B")
    require_uv_version(output("uv", "--version"))
    harness = load("provider_coverage").freeze_tree(ROOT, "pyshacl-turbo")
    for prefix in ("facade", "owlrl"):
        for suffix in ("source", "wheel"):
            name = prefix + "_" + suffix
            setattr(args, name, getattr(args, name).resolve(strict=True))
    args.output = args.output.resolve()
    if any(
        args.output.is_relative_to(source) for source in (args.facade_source, args.owlrl_source)
    ):
        raise ValueError("Candidate artifacts must remain outside frozen peer source checkouts")
    args.output.mkdir(parents=True, exist_ok=False)
    context = authority.prepare(args, args.output)
    receipt = context["receipt"]
    receipt["harness_source"] = harness
    if receipt["build_profile"]["maturin"]["profile"] != "release":
        raise ValueError("A DEBUG functional artifact is not eligible for timing builds")
    receipt.update(
        status="prepared",
        python=sys.version,
        uv=output("uv", "--version"),
        performance_eligible=False,
    )
    receipt_path = args.output / "candidate-build.json"
    isolated_output = args.output / "isolated-native-build"
    environment = build_environment(context["owner"])
    command = archive_command(context["archive"], isolated_output, sys.executable)
    launch = load("benchmark_launch").capture(
        environment, context["owner"], isolated_output, command
    )
    receipt["launch_configuration"] = launch
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    wheels = args.output / "candidate-wheels"
    wheels.mkdir()
    receipt["retained_peer_wheels"] = {
        prefix: str(
            copy_original_wheel(
                getattr(args, prefix + "_wheel"), wheels, getattr(args, prefix + "_wheel_sha256")
            )
        )
        for prefix in ("facade", "owlrl")
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    native_wheel = build_archive(
        context["archive"],
        wheels,
        isolated_output,
        environment=environment,
        python=sys.executable,
    )
    authority.verify_inputs(args, context)
    authority.verify_harness(ROOT, harness)
    if (
        load("benchmark_launch").capture(environment, context["owner"], isolated_output, command)
        != launch
    ):
        raise ValueError("Actual native build tools or launch configuration changed")
    installed = load("benchmark_candidate").verify(args, context, native_wheel, args.output)
    authority.verify_inputs(args, context)
    authority.verify_harness(ROOT, harness)
    receipt.update(status="verified", installed_candidate=installed, performance_eligible=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    write_worker_sources(receipt, receipt_path, wheels / "sources.json")


if __name__ == "__main__":
    main()
