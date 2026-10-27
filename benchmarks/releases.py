"""Versioned parse/infer/validate measurements using isolated native uv projects.

Uses the canonical companion workload and worker; no local source import is a
substitute for a wheel. The default reference and historical release are pinned.
Candidate wheel sets identify PR builds; released candidates resolve into a lock
that is preserved with the report. Each environment has its own dependency graph.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import random
import re
import shutil
import statistics
import subprocess
import sys
from datetime import UTC, datetime
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from upstream_support.process_launch import Popen

SPEC = importlib.util.spec_from_file_location(
    "companion_workloads", ROOT / "benchmarks/companions.py"
)
companions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(companions)
TURBO = {"rdflib-turbo", "owlrl-turbo", "pyshacl-turbo"}
REFERENCE = {"rdflib", "owlrl", "pyshacl"}


def harness_hashes():
    paths = [
        Path(__file__).resolve(),
        ROOT / "benchmarks/companions.py",
        ROOT / "benchmarks/inference_fanout.py",
        ROOT / "tests/upstream_support/process_launch.py",
    ]
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
    }


def command(arguments, *, timeout=600):
    with Popen(
        list(map(str, arguments)), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise RuntimeError(f"Command timeout after {timeout}s: {arguments}") from None
        if process.returncode:
            raise RuntimeError(
                f"Command failed ({process.returncode}): {arguments}\n{stdout}\n{stderr}"
            )
    return stdout


def validate_matrix(matrix):
    if matrix.get("schema") != 1:
        raise ValueError("Benchmark matrix schema must be 1")
    environments = matrix["environments"]
    if len(environments) < 2 or sum(env["backend"] == "reference" for env in environments) != 1:
        raise ValueError("Exactly one reference and at least one turbo environment are required")
    ids = set()
    for env in environments:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", env["id"]) or env["id"] in ids:
            raise ValueError("Environment IDs must be unique safe path components")
        ids.add(env["id"])
        if env["backend"] not in {"reference", "turbo", "turbo_shared", "published"}:
            raise ValueError("Unknown benchmark backend")
        required = REFERENCE if env["backend"] == "reference" else TURBO
        if not required <= env["requirements"].keys():
            raise ValueError("Every environment must declare all three products")
        for name, version in env["requirements"].items():
            if not re.fullmatch(r"[a-z0-9-]+", name) or not version.startswith(("==", ">=")):
                raise ValueError("Use explicit version requirements")
        if env["backend"] in {"reference", "turbo"} and any(
            not value.startswith("==") for value in env["requirements"].values()
        ):
            raise ValueError("Reference and historical versions must be exact")
    return environments


def wheel_set(directory):
    result = {}
    for wheel in sorted(directory.glob("*.whl")):
        with ZipFile(wheel) as archive:
            members = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            if len(members) != 1:
                raise ValueError(f"Invalid wheel metadata: {wheel}")
            metadata = BytesParser().parsebytes(archive.read(members[0]))
        name = metadata["Name"].lower().replace("_", "-")
        if name not in TURBO or name in result:
            raise ValueError(f"Expected exactly one wheel for each turbo product: {wheel}")
        result[name] = {
            "path": str(wheel.resolve()),
            "version": metadata["Version"],
            "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        }
    if result.keys() != TURBO:
        raise ValueError("Candidate wheel directory must contain all three turbo products")
    return result


def setup(env, directory, wheels, python):
    project = directory / env["id"]
    if project.exists():
        raise ValueError(f"Benchmark environments must be fresh: {project}")
    command(
        ["uv", "init", "--bare", "--no-workspace", "--vcs", "none", "--python", python, project]
    )
    command(["uv", "python", "pin", "--project", project, python])
    with (project / "pyproject.toml").open("a") as manifest:
        manifest.write('\n[tool.uv]\nprerelease = "allow"\n')
    requirements = [
        name + version
        for name, version in env["requirements"].items()
        if not (wheels and env["id"] == "candidate" and name in TURBO)
    ]
    if wheels and env["id"] == "candidate":
        requirements += [wheel["path"] for wheel in wheels.values()]
    command(
        [
            "uv",
            "add",
            "--project",
            project,
            "--no-sync",
            "--no-build",
            "--prerelease",
            "allow",
            *requirements,
        ]
    )
    command(["uv", "sync", "--project", project, "--locked", "--no-build"])
    executable = project / ".venv/bin/python"
    identity = json.loads(command([executable, "-I", Path(__file__), "--identity"]))
    for name, specifier in env["requirements"].items():
        expected = (
            wheels[name]["version"]
            if wheels and env["id"] == "candidate" and name in TURBO
            else specifier[2:]
        )
        if specifier.startswith("==") and identity["packages"][name]["version"] != expected:
            raise RuntimeError(f"Resolved version does not match {name}{specifier}")
    identity["uv_lock_sha256"] = hashlib.sha256((project / "uv.lock").read_bytes()).hexdigest()
    identity["uv_lock"] = str(Path("locks") / env["id"] / "uv.lock")
    return executable, identity


def identity():
    from importlib.metadata import distributions

    packages = {}
    for dist in distributions():
        name = dist.metadata["Name"].lower().replace("_", "-")
        packages[name] = {
            "version": dist.version,
            "origin": json.loads(dist.read_text("direct_url.json") or "null"),
            "native_sha256": {
                str(path): hashlib.sha256(dist.locate_file(path).read_bytes()).hexdigest()
                for path in dist.files or []
                if str(path).endswith((".so", ".pyd", ".dylib"))
            },
        }
    protocols = {}
    engines = {}
    if TURBO <= packages.keys():
        import pyshacl_turbo
        from rdflib_turbo import _native

        protocols = {
            "dataset": getattr(_native, "SHARED_SHACL_PROTOCOL", None),
            "validation": getattr(pyshacl_turbo, "SHARED_DATASET_PROTOCOL", None),
        }
        if any(value not in (None, 1) for value in protocols.values()):
            raise RuntimeError("Installed release declares an unsupported shared-dataset protocol")
        engines = {
            "dataset": getattr(_native, "SHACL_ENGINE_FINGERPRINT", None),
            "validation": getattr(pyshacl_turbo._native, "SHACL_ENGINE_FINGERPRINT", None),
            "dataset_engine_revision": getattr(_native, "SHACL_ENGINE_REVISION", None),
        }
        if (
            protocols == {"dataset": 1, "validation": 1}
            and engines["dataset"] != engines["validation"]
        ):
            raise RuntimeError("Installed wheels have different canonical SHACL engine sources")
    return {
        "shared_protocols": protocols,
        "engine_sources": engines,
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": packages,
    }


def measure(executable, job, repeats, memory_repeats, timeout):
    def sample(kind):
        return json.loads(
            command(
                [
                    executable,
                    "-I",
                    ROOT / "benchmarks/companions.py",
                    "--worker",
                    json.dumps(job),
                    "--repeats",
                    repeats,
                    "--measurement",
                    kind,
                ],
                timeout=timeout,
            )
        )

    timing = sample("time")
    memory = [sample("memory") for _ in range(memory_repeats)]
    if any(
        companions.without_report_text(value["observation"])
        != companions.without_report_text(timing["observation"])
        for value in memory
    ):
        raise RuntimeError(f"Cold/warm RDF mismatch: {job}")
    return {
        **timing,
        "median_ns": statistics.median(timing["samples_ns"]),
        "min_ns": min(timing["samples_ns"]),
        "max_ns": max(timing["samples_ns"]),
        "memory_samples": memory,
        "median_peak_rss_bytes": statistics.median(value["peak_rss_bytes"] for value in memory),
        "stable": timing["stable"]
        and all(value["observation"] == timing["observation"] for value in memory),
    }


def compare_runs(reference, candidate):
    return companions.comparison_for_runs(reference, candidate)


def release_jobs(sizes):
    pipelines = [
        {
            "case": "pipeline_" + mode,
            "mode": mode,
            "nodes": nodes,
            "operation": "pipeline_" + mode,
            "contract": "pipeline",
        }
        for nodes in sizes
        for mode in ("rdfs", "owlrl")
    ]
    return pipelines + [
        {
            "case": profile,
            "mode": "owlrl",
            "nodes": width,
            "operation": "owlrl",
            "fixture": profile,
            "contract": "inference",
        }
        for width in companions.FANOUT.WIDTHS
        for profile in companions.FANOUT.PROFILES
    ]


def add_logical_inplace_comparisons(row, environments, reference):
    """Add a separate logical transition result without changing raw parity."""
    if row["contract"] != "inference":
        return
    runs = row["environments"]
    row["logical_inplace_owlrl"] = {
        env["id"]: companions.FANOUT.logical_inplace_owlrl(
            runs[reference],
            runs[env["id"]],
            left_backend="reference",
            right_backend=env["backend"],
        )
        for env in environments
        if env["id"] != reference
    }
    row["logical_inplace_between_versions"] = {
        f"{left['id']} → {right['id']}": companions.FANOUT.logical_inplace_owlrl(
            runs[left["id"]],
            runs[right["id"]],
            left_backend=left["backend"],
            right_backend=right["backend"],
        )
        for i, left in enumerate(environments)
        for right in environments[i + 1 :]
        if left["backend"] != "reference" and right["backend"] != "reference"
    }


def require_standard_parity(reference, candidate, *, contract="pipeline"):
    left, right = reference["observation"], candidate["observation"]
    if left["closure"]["ordinary"] != right["closure"]["ordinary"]:
        raise RuntimeError("Shared candidate changed the ordinary RDF inference closure")
    if contract == "inference":
        required = {
            "complete_term_metadata",
            "initial_term_metadata",
            "namespaces_raw",
            "namespace_bindings",
            "public_effects",
            "decimal",
            "state",
        }
        if not required <= left.keys() or not required <= right.keys():
            raise RuntimeError("Missing complete inference-only observation")
        return
    if contract != "pipeline":
        raise ValueError("Unknown benchmark observation contract")
    if "report" not in left or "report" not in right:
        raise RuntimeError("Missing mandatory pipeline report")
    if (
        left["report"]["graph"] != right["report"]["graph"]
        or left["report"]["conforms"] != right["report"]["conforms"]
    ):
        raise RuntimeError("Shared candidate changed the complete validation report graph")


def write_report(report, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    lines = [
        "# Versioned shared-dataset pipeline benchmarks",
        "",
        report["method"],
        "",
        f"Measured: {report['date']}; platform: {platform.platform()}.",
        f"Harness revision: `{report['source_revision']}`; dirty source tree: `{report['source_tree_dirty']}`. Candidate wheel source revisions and hashes are retained in the raw evidence.",
        "",
        "| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |",
        "|---|---:|---|---:|---:|---:|---|---:|---|---:|",
    ]
    for row in report["runs"]:
        for name, value in row["environments"].items():
            comparison = row.get("comparisons", {}).get(name, {})
            ratio = comparison.get("speedup")
            scoped = row.get("logical_inplace_owlrl", {}).get(name, {})
            scoped_ratio = scoped.get("speedup")
            lines.append(
                f"| {row['case']} | {row['nodes']} | {name} | {value['median_ns'] / 1e6:.3f} | {value['min_ns'] / 1e6:.3f}–{value['max_ns'] / 1e6:.3f} | {value['median_peak_rss_bytes'] / 2**20:.2f} | {comparison.get('status', 'reference')} | {f'{ratio:.2f}×' if ratio is not None else '—'} | {scoped.get('status', '—')} | {f'{scoped_ratio:.2f}×' if scoped_ratio is not None else '—'} |"
            )
    lines += ["", "## Exact product versions", ""]
    for name, env in report["environments"].items():
        packages = env["identity"]["packages"]
        products = REFERENCE if env["backend"] == "reference" else TURBO
        lines.append(
            f"- {name}: "
            + ", ".join(f"{product} {packages[product]['version']}" for product in sorted(products))
        )
    if "error" in report:
        lines += ["", f"**Failed: {report['error']}**"]
    lines += [
        "",
        "Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.",
        "Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.",
        "",
    ]
    output.with_suffix(".md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=ROOT / "benchmarks/releases.json")
    parser.add_argument("--candidate-wheels", type=Path)
    parser.add_argument("--python", default="3.13")
    parser.add_argument("--nodes", type=int, nargs="+", default=[100, 1000])
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--memory-repeats", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--integration-tests", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "benchmark-artifacts/releases.json")
    parser.add_argument("--identity", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.identity:
        print(json.dumps(identity()))
        return
    if min(args.nodes) <= 0 or min(args.repeats, args.memory_repeats) <= 0 or args.timeout <= 0:
        parser.error("Sizes, repeats and timeout must be positive")
    companions.rss_bytes(0, sys.platform)
    envs = validate_matrix(json.loads(args.matrix.read_text()))
    wheels = wheel_set(args.candidate_wheels) if args.candidate_wheels else None
    output = args.output.resolve()
    report = {
        "schema": 1,
        "date": datetime.now(UTC).isoformat(),
        "environments": {},
        "runs": [],
        "matrix": json.loads(args.matrix.read_text()),
        "candidate_wheels": wheels,
        "candidate_sources": json.loads((args.candidate_wheels / "sources.json").read_text())
        if args.candidate_wheels and (args.candidate_wheels / "sources.json").exists()
        else None,
        "source_tree_dirty": bool(command(["git", "-C", ROOT, "status", "--porcelain"])),
        "host": {"logical_cpus": os.cpu_count(), "load_average_start": os.getloadavg()},
        "source_revision": command(["git", "-C", ROOT, "rev-parse", "HEAD"]).strip(),
        "uv_version": command(["uv", "--version"]).strip(),
        "harness_sha256": harness_hashes(),
        "method": "Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.",
    }
    executables = {}
    reference = next(env["id"] for env in envs if env["backend"] == "reference")
    try:
        for env in envs:
            executable, installed = setup(env, output.parent / "environments", wheels, args.python)
            if env["backend"] == "published":
                # Classify the installed release's declared capabilities before
                # measurement. Never retry a failing shared operation via conversion.
                env["backend"] = (
                    "turbo_shared"
                    if installed["shared_protocols"] == {"dataset": 1, "validation": 1}
                    else "turbo"
                )
            executables[env["id"]] = executable
            report["environments"][env["id"]] = {"backend": env["backend"], "identity": installed}
        if args.integration_tests:
            candidate = output.parent / "environments/candidate"
            original = next(env for env in envs if env["backend"] == "reference")
            command(
                [
                    "uv",
                    "add",
                    "--project",
                    candidate,
                    "--no-build",
                    "pytest==9.1.1",
                    *[name + pin for name, pin in original["requirements"].items()],
                ]
            )
            command([executables["candidate"], "-I", "-m", "pytest", args.integration_tests, "-q"])
            installed = json.loads(
                command([executables["candidate"], "-I", Path(__file__), "--identity"])
            )
            installed["uv_lock_sha256"] = hashlib.sha256(
                (candidate / "uv.lock").read_bytes()
            ).hexdigest()
            installed["uv_lock"] = "locks/candidate/uv.lock"
            report["environments"]["candidate"]["identity"] = installed
        # Builds, installs, and integration tests finish before any timed worker.
        rng = random.Random(20261017)
        for job in release_jobs(args.nodes):
            row = {
                "case": job["case"],
                "mode": job["mode"],
                "nodes": job["nodes"],
                "contract": job["contract"],
                "environments": {},
                "comparisons": {},
            }
            report["runs"].append(row)
            order = list(envs)
            rng.shuffle(order)
            for env in order:
                row["environments"][env["id"]] = measure(
                    executables[env["id"]],
                    {
                        **{
                            key: value
                            for key, value in job.items()
                            if key not in {"case", "contract", "mode"}
                        },
                        "backend": env["backend"],
                        "observation_encoder": "unique-anchors-v1",
                    },
                    args.repeats,
                    args.memory_repeats,
                    args.timeout,
                )
            ref = row["environments"][reference]
            for env in envs:
                if env["id"] == reference:
                    continue
                value = row["environments"][env["id"]]
                row["comparisons"][env["id"]] = compare_runs(ref, value)
                if env["backend"] == "turbo_shared":
                    require_standard_parity(ref, value, contract=job["contract"])
            # Preserve direct release-to-release comparisons separately.
            row["between_versions"] = {
                f"{left['id']} → {right['id']}": compare_runs(
                    row["environments"][left["id"]], row["environments"][right["id"]]
                )
                for i, left in enumerate(envs)
                for right in envs[i + 1 :]
                if left["backend"] != "reference" and right["backend"] != "reference"
            }
            add_logical_inplace_comparisons(row, envs, reference)
            write_report(report, output)
            print(f"Measured {job['case']}/{job['nodes']}", flush=True)
    except Exception as error:
        report["error"] = str(error)
        write_report(report, output)
        raise
    finally:
        report["host"]["load_average_end"] = os.getloadavg()
        # Retain manifests/locks, never publish virtual environments or executables.
        for executable in executables.values():
            project = executable.parents[2]
            destination = output.parent / "locks" / project.name
            destination.mkdir(parents=True, exist_ok=True)
            for name in ("uv.lock", "pyproject.toml", ".python-version"):
                shutil.copy2(project / name, destination / name)
    write_report(report, output)


if __name__ == "__main__":
    main()
