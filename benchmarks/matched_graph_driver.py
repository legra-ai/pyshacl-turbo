"""Native-UV replay of matched Graph pipelines, separate from old12 workloads."""

import argparse
import importlib.util
import json
import platform
import shutil
import sys
import time
from pathlib import Path

ENTRY_PERF_NS = time.perf_counter_ns()
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "matched_driver_authority", Path(__file__).with_name("matched_graph_authority.py")
)
AUTHORITY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTHORITY)
WORKER = AUTHORITY.load("matched_graph_worker")
RELEASES = AUTHORITY.RELEASES


def validate_cohort(matrix):
    environments = RELEASES.validate_matrix(matrix)
    roles = {entry["role"]: entry for entry in environments}
    if len(roles) != len(environments) or set(roles) != {
        "reference",
        "baseline",
        "latest-compatible-released",
    }:
        raise ValueError(
            "Cohort requires distinct reference, baseline and latest-compatible-released roles"
        )
    if (
        roles["reference"]["backend"] != "reference"
        or roles["baseline"]["backend"] != "turbo"
        or roles["latest-compatible-released"]["backend"] != "published"
    ):
        raise ValueError("Cohort role/backend authority differs")
    return roles


def iteration_order(repeats):
    if type(repeats) is not int or not 5 <= repeats <= 31:
        raise ValueError("Retain5..31 fresh samples per arm")
    # bounded: at most64 launches per closed synthetic case.
    return [
        ("warmup" if index == 0 else f"sample{index}", backend)
        for index in range(repeats + 1)
        for backend in (["reference", "turbo"] if index % 2 == 0 else ["turbo", "reference"])
    ]


def child(project, job, proof, python):
    command = [
        "uv",
        "run",
        "--project",
        project,
        "--python",
        python,
        "--locked",
        "--no-sync",
        "--no-build",
        "python",
        "-I",
        "-B",
        Path(__file__),
        "--worker",
        json.dumps(job),
        "--proof",
        proof,
    ]
    start = time.perf_counter_ns()
    stdout = RELEASES.command(command, timeout=90)
    result = json.loads(stdout)
    result.update(launch_perf_ns=start, parent_child_wall_ns=time.perf_counter_ns() - start)
    result["argv"] = list(map(str, command))
    return result


def check_case(invoke, projects, width, profile, output):
    case = {"width": width, "profile": profile, "oracles": {}, "diagnostics": {}}
    for normalize in [False, True]:
        observations = []
        for backend in ["reference", "turbo"]:
            proof = output / f"correctness-{normalize}-{backend}.json.gz"
            invoke(
                projects[backend],
                {
                    "kind": "correctness",
                    "backend": backend,
                    "width": width,
                    "profile": profile,
                    "normalize": normalize,
                },
                proof,
            )
            observation = WORKER.read_proof(proof)["observation"]
            observations.append(observation)
            if normalize:
                case["oracles"][backend] = str(proof.resolve())
        gate = WORKER.SAMPLER.CONTRACT.comparison(*observations)
        case["diagnostics"][str(normalize)] = gate
        if gate["status"] == "error":
            raise RuntimeError("Public correctness operation returned an error")
        if normalize:
            case["normal"] = gate
    return case


def sample_case(invoke, projects, case, output, repeats):
    if case["normal"]["status"] != "equal":
        raise RuntimeError("Normal-policy complete correctness must pass before sampling")
    samples = {backend: [] for backend in ["reference", "turbo"]}
    for role, backend in iteration_order(repeats):
        proof = output / f"{backend}-{role}.json.gz"
        invoke(
            projects[backend],
            {
                "kind": "sample",
                "backend": backend,
                "width": case["width"],
                "profile": case["profile"],
                "oracle": case["oracles"][backend],
            },
            proof,
        )
        value = WORKER.read_proof(proof)
        if value["gate"]["status"] != "equal":
            raise RuntimeError("Timed postconditions differ; ratios withheld")
        if role != "warmup":
            samples[backend].append(value)
    return WORKER.SAMPLER.summarize(samples["reference"], samples["turbo"])


def harness_hashes(cohort):
    paths = [
        Path(__file__),
        Path(cohort),
        *(
            ROOT / "benchmarks" / name
            for name in [
                "matched_graph_authority.py",
                "matched_graph_worker.py",
                "matched_graph_sampling.py",
                "matched_graph_fanout.py",
            ]
        ),
    ]
    return {
        **RELEASES.harness_hashes(),
        **{
            path.relative_to(ROOT).as_posix()
            if path.is_relative_to(ROOT)
            else "cohort_input": AUTHORITY.sha(path)
            for path in paths
        },
    }


def proof_hashes(output):
    return {
        str(path.relative_to(output)): AUTHORITY.sha(path)
        for directory in ["proofs", "locks", "originals"]
        for path in (output / directory).rglob("*")
        if path.is_file()
    }


def run(args):
    if args.python != "3.13.16" or RELEASES.command(["uv", "--version"]).split()[1] != "0.13.5":
        raise RuntimeError("Use native UV0.13.5 and CPython3.13.16")
    iteration_order(args.repeats)
    if len(set(args.roles)) != len(args.roles):
        raise ValueError("Cohort roles must be unique")
    if any(width not in [32, 128, 512, 1000] for width in args.widths) or len(
        set(args.widths)
    ) != len(args.widths):
        raise ValueError("Widths must be unique members of32,128,512,1000")
    environments = validate_cohort(json.loads(args.cohort.read_text()))
    locks = {}
    for value in args.lock_input:
        role, path = value.split("=", 1)
        if role not in {"reference", *args.roles} or role in locks:
            raise ValueError("Replay lock has a foreign or duplicate role")
        locks[role] = Path(path).resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    projects, before, originals, keys = {}, {}, {}, {}
    record = {
        "schema": 1,
        "contract": "matched-public-graph-pipeline-v1",
        "status": "incomplete",
        "python": sys.version,
        "host": platform.platform(),
        "cohort": json.loads(args.cohort.read_text()),
        "harness": harness_hashes(args.cohort),
        "roles": {},
        "cases": [],
        "commands": [],
    }
    invoke = lambda project, job, proof: _record_child(record, project, job, proof, args.python)
    try:
        for role in ["reference", *args.roles]:
            project, identity = AUTHORITY.setup(
                environments[role], output, args.python, Path(__file__), locks.get(role)
            )
            projects[role], before[role] = project, identity
            originals[role] = AUTHORITY.capture_originals(project, identity, output / "originals")
            keys[role] = AUTHORITY.cohort_key(originals[role])
            record["roles"][role] = {
                "identity": identity,
                "original_wheels": originals[role],
                "whole_wheel_cohort": keys[role],
            }
            lock_dir = output / "locks" / role
            lock_dir.mkdir(parents=True)
            shutil.copyfile(project / "uv.lock", lock_dir / "uv.lock")
            shutil.copyfile(project / "pyproject.toml", lock_dir / "pyproject.toml")
        measured = {}
        for role in args.roles:
            if keys[role] in measured:
                record["roles"][role]["deduplicated_from"] = measured[keys[role]]
                continue
            measured[keys[role]] = role
            paired = {"reference": projects["reference"], "turbo": projects[role]}
            cases = []
            for width in args.widths:
                for profile in ["literal-reflexivity", "literal-type"]:
                    directory = output / "proofs" / role / f"{width}-{profile}"
                    directory.mkdir(parents=True)
                    case = check_case(invoke, paired, width, profile, directory)
                    case["role"] = role
                    record["cases"].append(case)
                    cases.append((case, directory))
            if any(case["normal"]["status"] != "equal" for case, _ in cases):
                raise RuntimeError(
                    "Complete normal-policy correctness failed; no cohort timing started"
                )
            if not args.correctness_only:
                for case, directory in cases:
                    case["samples"] = sample_case(invoke, paired, case, directory, args.repeats)
        record["status"] = "complete"
    finally:
        after = {
            role: AUTHORITY.identity(project, args.python, Path(__file__))
            for role, project in projects.items()
        }
        record["identities_after"] = after
        record["guards_equal"] = before == after and record["harness"] == harness_hashes(
            args.cohort
        )
        record["proof_sha256"] = proof_hashes(output)
        (output / "summary.json").write_text(json.dumps(record, indent=2))
        (output / "summary.md").write_text(markdown(record))
        if not record["guards_equal"]:
            raise RuntimeError("Full installed payload/project/harness identity changed")
    return record


def _record_child(record, project, job, proof, python):
    result = child(project, job, proof, python)
    record["commands"].append({"job": job, **result})
    return result


def markdown(record):
    lines = [
        "# Matched public Graph pipelines",
        "",
        "Imports, fixture text and SHAPES are prepared outside the public construct/parse → class expand → validate interval. Absolute process RSS is captured before full observation encoding. NORMALIZE=False diagnostics remain separate; no full-drop-in claim.",
        "",
        "| Role | Width | Profile | Normal gate | False gate | Total speed ratio | Absolute RSS reduction |",
        "|---|---:|---|---|---|---:|---:|",
    ]
    for role, entry in record["roles"].items():
        names = RELEASES.REFERENCE if role == "reference" else RELEASES.TURBO
        versions = {name: entry["identity"]["packages"][name]["version"] for name in sorted(names)}
        lines.insert(
            3,
            f"Resolved {role}: {versions}; whole-wheel cohort {entry['whole_wheel_cohort']}; execution reuse: {entry.get('deduplicated_from', 'none')}.",
        )
    for case in record["cases"]:
        samples = case.get("samples", {})
        lines.append(
            f"| {case['role']} | {case['width']} | {case['profile']} | {case['normal']['status']} | {case['diagnostics']['False']['status']} | {samples.get('speedup')} | {samples.get('rss_reduction')} |"
        )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cohort", type=Path, default=ROOT / "benchmarks/matched-graph-releases.json"
    )
    parser.add_argument(
        "--roles",
        nargs="+",
        choices=["baseline", "latest-compatible-released"],
        default=["baseline", "latest-compatible-released"],
    )
    parser.add_argument("--lock-input", action="append", default=[], metavar="ROLE=LOCK")
    parser.add_argument("--widths", nargs="+", type=int, default=[32, 128, 512, 1000])
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--python", default="3.13.16")
    parser.add_argument("--output", type=Path, default=Path("benchmark-artifacts/matched-graph"))
    parser.add_argument("--correctness-only", action="store_true")
    parser.add_argument("--worker", help=argparse.SUPPRESS)
    parser.add_argument("--proof", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--identity", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.identity:
        print(json.dumps(AUTHORITY.installed_identity()))
    elif args.worker:
        print(json.dumps(WORKER.execute(json.loads(args.worker), args.proof, ENTRY_PERF_NS)))
    else:
        run(args)


if __name__ == "__main__":
    main()
