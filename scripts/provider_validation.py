"""Validate a pure original facade wheel against its published native authority."""

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require_output(source, output):
    if output.resolve().is_relative_to(source.resolve()):
        raise ValueError("Validation output must remain outside frozen facade source")


def environment():
    result = {
        name: value
        for name, value in os.environ.items()
        if not name.startswith(("UV_", "PIP_", "PYTHON")) and name != "VIRTUAL_ENV"
    }
    result.update(
        UV_NO_CONFIG="1",
        UV_NO_BUILD="1",
        UV_PYTHON=sys.executable,
        PYTHONDONTWRITEBYTECODE="1",
    )
    return result


def run(command, *, directory=None, env=None, capture=False):
    # The registry probe installs the macOS no-fork launcher. Change the parent
    # directory explicitly instead of asking subprocess to use fork-only cwd=.
    with contextlib.chdir(directory) if directory else contextlib.nullcontext():
        result = subprocess.run(
            list(map(str, command)),
            check=True,
            env=env,
            capture_output=capture,
            text=True,
        )
    return result.stdout if capture else None


def installed_probe(owner, wheel, project):
    registry = load("check_registry_pair")
    return (
        registry.PROBE
        + registry.RECEIPT_PROBE
        + f"""
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("native_owner", {str(owner / "scripts/native_coverage.py")!r})
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
print(json.dumps(collector.verify_loaded_facade(Path({str(wheel)!r}), Path({str(project / ".venv")!r}))))
"""
    )


def test_command(source, project, output, *, coverage):
    command = [
        "uv",
        "run",
        "--project",
        str(project),
        "--locked",
        "--no-sync",
        "python",
        "-I",
        "-m",
        "pytest",
        str(source / "tests"),
        "-q",
        "--import-mode=importlib",
    ]
    if coverage:
        command.extend(
            [
                "--cov=pyshacl_turbo",
                "--cov-branch",
                "--cov-fail-under=100",
                f"--cov-report=json:{output / 'python-coverage.json'}",
                f"--cov-report=xml:{output / 'python-coverage.xml'}",
                f"--cov-report=html:{output / 'htmlcov'}",
            ]
        )
    return command


def verify_acceptance_binding(frozen, actual):
    if actual["revision"] != frozen["revision"] or actual["source_sha256"] != frozen["files"]:
        raise ValueError("Native owner did not bind the exact current acceptance source")


def installed_receipts(owner, wheel, project, env):
    evidence = run(
        [
            "uv",
            "run",
            "--project",
            project,
            "--locked",
            "--no-sync",
            "python",
            "-I",
            "-c",
            installed_probe(owner, wheel, project),
        ],
        env=env,
        capture=True,
    )
    return [json.loads(line) for line in evidence.strip().splitlines()[-2:]]


def verify_runtime(context):
    native, facade = installed_receipts(
        context["owner"], context["wheel"], context["project"], context["environment"]
    )
    if (
        native != context["receipt"]["installed_provider"]
        or facade != context["receipt"]["installed_facade"]
    ):
        raise ValueError("Installed runtime payload changed during validation")


def prepare(source, wheel, output):
    source, wheel, output = (
        source.resolve(strict=True),
        wheel.resolve(strict=True),
        output.resolve(),
    )
    require_output(source, output)
    frozen = load("provider_coverage").freeze_tree(source, "pyshacl-turbo")
    output.mkdir(parents=True, exist_ok=False)
    authority = load("published_provider").resolve(source, wheel, output / "provider")
    owner = Path(authority["source"])
    acceptance = owner.parent / "current-facade"
    run(["git", "clone", "--no-checkout", source, acceptance])
    run(["git", "-C", acceptance, "checkout", "--detach", frozen["revision"]])
    if load("provider_coverage").freeze_tree(acceptance, "pyshacl-turbo") != frozen:
        raise ValueError("Current acceptance checkout differs from the original facade source")
    spec = importlib.util.spec_from_file_location(
        "native_owner", owner / "scripts/native_coverage.py"
    )
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    if not callable(getattr(collector, "facade_source_payload", None)):
        raise TypeError("Published native owner lacks portable facade payload verification")
    facade_inputs = {
        "revision": frozen["revision"],
        "source_sha256": frozen["files"],
        "package_payload": collector.facade_source_payload(acceptance, wheel),
        "wheel_sha256": digest(wheel),
    }
    verify_acceptance_binding(frozen, facade_inputs)
    env = environment()
    project = output / "project"
    run(["uv", "init", "--bare", "--no-workspace", "--vcs", "none", project], env=env)
    run(["uv", "python", "pin", "--project", project, sys.executable], env=env)
    run(
        [
            "uv",
            "add",
            "--project",
            project,
            "--no-sync",
            "--extra",
            "test",
            "--default-index",
            "https://pypi.org/simple",
            wheel,
        ],
        env=env,
    )
    lock = tomllib.loads((project / "uv.lock").read_text())
    providers = [package for package in lock["package"] if package["name"] == "rdflib-turbo"]
    if (
        len(providers) != 1
        or providers[0]["source"] != {"registry": "https://pypi.org/simple"}
        or providers[0]["version"] != authority["provider_version"]
    ):
        raise ValueError("Validation must install the exact published native provider")
    run(["uv", "sync", "--project", project, "--locked"], env=env)
    native, facade = installed_receipts(owner, wheel, project, env)
    expected = json.loads((output / "provider/registry-capability.json").read_text())
    if (
        native != expected
        or facade["engine_fingerprint"] != authority["identity"]["engine_fingerprint"]
    ):
        raise ValueError("Installed pair differs from independently verified published authority")
    receipt = {
        "current_facade": frozen,
        "facade_inputs": facade_inputs,
        "provider": authority,
        "installed_provider": native,
        "installed_facade": facade,
        "environment_lock_sha256": digest(project / "uv.lock"),
    }
    (output / "installed-pair.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    return {
        "source": source,
        "wheel": wheel,
        "acceptance": acceptance,
        "owner": owner,
        "project": project,
        "output": output,
        "environment": env,
        "receipt": receipt,
    }


def verify_sources(context):
    receipt, output = context["receipt"], context["output"]
    verify_runtime(context)
    roots = (context["source"], context["acceptance"])
    if any(
        load("provider_coverage").freeze_tree(root, "pyshacl-turbo") != receipt["current_facade"]
        for root in roots
    ):
        raise ValueError("Frozen current facade acceptance inputs changed")
    provider = receipt["provider"]
    registry = load("provider_registry")
    registry.verify_extracted(
        Path(provider["source_archive"]),
        context["owner"],
        provider["source_sha256"],
        exact_inventory=False,
    )
    for peer in (provider["peers"]["declaration_peer"], provider["peers"]["owlrl"]):
        if (
            registry.verify_extracted(
                Path(peer["archive"]), Path(peer["source"]), peer["sha256"], exact_inventory=False
            )
            != peer["files"]
        ):
            raise ValueError("Original published peer changed during validation")
    if digest(context["project"] / "uv.lock") != receipt["environment_lock_sha256"]:
        raise ValueError("Installed validation lock changed")
    (output / "validation-verified.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facade-source", type=Path, required=True)
    parser.add_argument("--facade-wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--coverage", action="store_true")
    args = parser.parse_args()
    context = prepare(args.facade_source, args.facade_wheel, args.output)
    env = {**context["environment"], "COVERAGE_FILE": str(args.output / "python.coverage")}
    run(
        test_command(
            context["acceptance"], context["project"], args.output, coverage=args.coverage
        ),
        directory=context["acceptance"],
        env=env,
    )
    for check in (["check"], ["format", "--check"]):
        run(
            [
                "uv",
                "run",
                "--project",
                context["acceptance"],
                "--locked",
                "--only-group",
                "dev",
                "ruff",
                *check,
                "python",
                "tests",
                "benchmarks",
                "scripts",
            ],
            directory=context["acceptance"],
            env=env,
        )
    verify_sources(context)


if __name__ == "__main__":
    main()
