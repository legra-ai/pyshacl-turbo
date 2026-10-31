"""Build measurement inputs only from the exact declared published native authority."""

import argparse
import importlib.util
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pure_artifacts(source, output):
    validation = load("provider_validation")
    env = validation.environment()
    del env["UV_NO_BUILD"]
    originals = output / "facade-originals"
    validation.run(
        ["uv", "build", "--sdist", "--python", sys.executable, "--out-dir", originals, source],
        env=env,
    )
    archives = list(originals.glob("*.tar.gz"))
    if len(archives) != 1:
        raise ValueError("Expected one original pure facade source archive")
    wheel = load("build_benchmark_wheels").build_archive(
        archives[0],
        originals,
        output / "isolated-pure-build",
        environment=env,
        python=sys.executable,
    )
    validation.run(
        [sys.executable, "-B", ROOT / "scripts/check_package.py", archives[0], wheel], env=env
    )
    return archives[0], wheel


def original_owl_wheel(owl, output):
    registry = load("provider_registry")
    document_path = Path(owl["registry_document"])
    document = json.loads(document_path.read_text())
    if (
        registry.select_source(document, "owlrl-turbo", owl["version"])["digests"]["sha256"]
        != owl["sha256"]
    ):
        raise ValueError("Retained OWL registry record differs from the locked original source")
    entry = registry.select_universal(document, "owlrl-turbo", owl["version"])
    originals = output / "owl-originals"
    originals.mkdir()
    wheel = registry.download(entry, originals)
    return {
        "path": str(wheel),
        "sha256": entry["digests"]["sha256"],
        "registry_document_sha256": load("provider_validation").digest(document_path),
    }


def builder_arguments(
    source, revision, facade_wheel, provider, owl_wheel, output, *, execution_owlrl
):
    owl = execution_owlrl
    return list(
        map(
            str,
            [
                sys.executable,
                "-B",
                ROOT / "scripts/build_benchmark_wheels.py",
                "--provider-archive",
                provider["source_archive"],
                "--provider-sha256",
                provider["source_sha256"],
                "--facade-source",
                source,
                "--facade-revision",
                revision,
                "--facade-wheel",
                facade_wheel,
                "--facade-wheel-sha256",
                load("provider_validation").digest(facade_wheel),
                "--owlrl-source",
                owl["source"],
                "--owlrl-archive",
                owl["archive"],
                "--owlrl-archive-sha256",
                owl["sha256"],
                "--owlrl-wheel",
                owl_wheel["path"],
                "--owlrl-wheel-sha256",
                owl_wheel["sha256"],
                "--output",
                output,
            ],
        )
    )


def prepare(source, output):
    validation = load("provider_validation")
    validation.require_output(source, output)
    frozen = load("provider_coverage").freeze_tree(source, "pyshacl-turbo")
    if (
        tomllib.loads((source / "pyproject.toml").read_text())["build-system"]["build-backend"]
        != "hatchling.build"
    ):
        raise ValueError("Production pipeline inputs require the pure facade build backend")
    output.mkdir(parents=True, exist_ok=False)
    request = {"facade_source": frozen, "status": "preparing-original-pure-inputs"}
    receipt = output / "published-benchmark-request.json"
    receipt.write_text(json.dumps(request, indent=2) + "\n")
    archive, wheel = pure_artifacts(source, output)
    if load("provider_coverage").freeze_tree(source, "pyshacl-turbo") != frozen:
        raise ValueError("Frozen facade source changed during its original archive build")
    # Registry capability precedes every OWL download and native compilation.
    provider = load("published_provider").resolve(source, wheel, output / "published-provider")
    execution_owl = load("published_peers").execution_peer(
        source, Path(provider["source"]), output / "execution-owlrl"
    )
    owl_wheel = original_owl_wheel(execution_owl, output)
    request.update(
        status="published-originals-verified",
        facade_archive=str(archive),
        facade_wheel=str(wheel),
        provider=provider,
        execution_owlrl=execution_owl,
        owlrl_wheel=owl_wheel,
    )
    receipt.write_text(json.dumps(request, indent=2) + "\n")
    return frozen, wheel, provider, owl_wheel, execution_owl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facade-source", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not sys.dont_write_bytecode:
        raise ValueError("Published original benchmark inputs require python -B")
    source, output = args.facade_source.resolve(strict=True), args.output.resolve()
    frozen, wheel, provider, owl, execution_owl = prepare(source, output)
    command = builder_arguments(
        source,
        frozen["revision"],
        wheel,
        provider,
        owl,
        output / "candidate",
        execution_owlrl=execution_owl,
    )
    load("provider_validation").run(command, env=load("provider_validation").environment())
    if load("provider_coverage").freeze_tree(source, "pyshacl-turbo") != frozen:
        raise ValueError("Frozen facade source changed during published input preparation")


if __name__ == "__main__":
    main()
