"""Verify original candidate wheels in a fresh native uv project before timing."""

import importlib.util
import json
import sys
import tomllib
from pathlib import Path


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_lock(lock, project, wheels):
    for name, wheel in wheels.items():
        packages = [package for package in lock["package"] if package["name"] == name]
        if len(packages) != 1 or set(packages[0]["source"]) != {"path"}:
            raise ValueError("Candidate UV lock must use each exact original wheel")
        selected = Path(packages[0]["source"]["path"])
        if not selected.is_absolute():
            selected = project / selected
        if selected.resolve() != wheel.resolve():
            raise ValueError("Candidate UV lock must use each exact original wheel")


def probe(owner, facade_wheel, native_wheel, project):
    registry = load("check_registry_pair")
    sha256 = load("provider_validation").digest(native_wheel)
    return (
        registry.probe(registry.InstallationMode.CANDIDATE, native_wheel, sha256)
        + registry.RECEIPT_PROBE
        + f"""
import importlib.util
import owlrl_turbo
spec = importlib.util.spec_from_file_location("original_owner_collector", {str(owner / "scripts/native_coverage.py")!r})
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
print(json.dumps(collector.verify_loaded_facade(Path({str(facade_wheel)!r}), Path({str(project / ".venv")!r}))))
package = distribution("owlrl-turbo")
root = Path(owlrl_turbo.__file__).resolve().parent
if not root.is_relative_to(Path({str(project / ".venv")!r}).resolve()):
    raise RuntimeError("OWL candidate loaded outside the isolated wheel project")
payload = {{str(name): digest(Path(package.locate_file(name))) for name in package.files if str(name).startswith("owlrl_turbo/") and not str(name).endswith(".pyc")}}
print(json.dumps({{"payload": payload, "version": package.version}}))
"""
    )


def verify(args, context, native_wheel, output):
    validation = load("provider_validation")
    env = validation.environment()
    project = output / "project"
    wheels = {
        "rdflib-turbo": native_wheel,
        "pyshacl-turbo": args.facade_wheel,
        "owlrl-turbo": args.owlrl_wheel,
    }
    validation.run(["uv", "init", "--bare", "--no-workspace", "--vcs", "none", project], env=env)
    validation.run(["uv", "python", "pin", "--project", project, sys.executable], env=env)
    validation.run(
        [
            "uv",
            "add",
            "--project",
            project,
            "--no-sync",
            "--default-index",
            "https://pypi.org/simple",
            *wheels.values(),
        ],
        env=env,
    )
    lock_path = project / "uv.lock"
    verify_lock(tomllib.loads(lock_path.read_text()), project, wheels)
    validation.run(["uv", "sync", "--project", project, "--locked"], env=env)
    result = validation.run(
        [
            "uv",
            "run",
            "--project",
            project,
            "--locked",
            "--no-sync",
            "python",
            "-I",
            "-B",
            "-c",
            probe(context["owner"], args.facade_wheel, native_wheel, project),
        ],
        env=env,
        capture=True,
    )
    records = [json.loads(line) for line in result.strip().splitlines()]
    if len(records) != 4:
        raise ValueError("Expected all four complete installed candidate receipts")
    public, native, facade, owl = records
    load("benchmark_owner").verify_engine(context["receipt"]["source_identity"], public)
    load("benchmark_owner").verify_engine(context["receipt"]["source_identity"], native)
    if (
        facade["engine_fingerprint"] != native["fingerprint"]
        or owl["payload"] != context["receipt"]["peers"]["owlrl"]["payload"]
    ):
        raise ValueError("Installed candidate peer payload or engine identity mismatch")
    load("published_provider").verify_wheel(native_wheel, native)
    load("published_provider").verify_source_package(
        context["owner"], native["payload"], native["native_member"]
    )
    receipt = {
        "purpose": "functional-original-wheel-verification",
        "installed_provider": native,
        "installed_facade": facade,
        "installed_owlrl": owl,
        "project_lock_sha256": validation.digest(lock_path),
        "original_wheels": {
            name: {"path": str(path), "sha256": validation.digest(path)}
            for name, path in wheels.items()
        },
    }
    (output / "installed-candidate.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt
