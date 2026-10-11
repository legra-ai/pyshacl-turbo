"""Alternate isolated packages to diagnose structural compiler overhead.

Fresh subprocesses select each prebuilt extension; startup and fixture creation
are outside timing. No native extension is imported by the parent process.
"""

import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def worker(repeats):
    import matrix
    from pyshacl_turbo import _native

    case = matrix.make_case("shapes", 1000, 1000)
    data, shapes = case["data"], case["shapes"]
    matrix.require_same_report(
        matrix.pyshacl.validate(data, shacl_graph=shapes),
        matrix.turbo.validate(data, shacl_graph=shapes),
        case["name"],
    )
    package_root = Path(os.environ["PYTHONPATH"]).resolve()
    if not Path(_native.__file__).resolve().is_relative_to(package_root):
        raise RuntimeError("The worker did not load the requested native package")
    source = matrix.turbo._input(shapes, flatten=True)
    namespaces = [(p, str(ns)) for p, ns in shapes.namespaces()]
    runners = {
        "python_api_compile": lambda: matrix.turbo.compile_shapes(shapes),
        "native_compile": lambda: _native.CompiledShapes(
            source.source, source.format, source.base, False, True, namespaces
        ),
    }
    for runner in runners.values():
        runner()
    return {
        "native_path": _native.__file__,
        "native_sha256": hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),
        "reports_isomorphic": True,
        "phases": matrix.time_calls(runners, repeats),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-package", type=Path)
    parser.add_argument("--candidate-package", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--rounds", type=int, default=4)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.repeats < 1 or args.rounds < 1:
        parser.error("rounds and repeats must be positive")
    if args.worker:
        print(json.dumps(worker(args.repeats)))
        return
    if not all([args.baseline_package, args.candidate_package, args.output]):
        parser.error("both package roots and --output are required")
    result = {
        "date": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "workload": "1,000 node shapes plus 1,000 attached property shapes; 1,000 data nodes",
        "load_note": "No concurrent task builds/tests. Other-workspace builds remain active; samples are descriptive.",
        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "rounds": [],
    }
    packages = {"before": args.baseline_package, "after": args.candidate_package}
    for round_index in range(args.rounds):
        names = list(packages) if round_index % 2 == 0 else list(reversed(packages))
        for name in names:
            env = dict(os.environ, PYTHONPATH=str(packages[name].resolve()))
            process = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--worker",
                    "--repeats",
                    str(args.repeats),
                ],
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
            result["rounds"].append(
                {"round": round_index, "variant": name, **json.loads(process.stdout)}
            )
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(f"Finished paired round {round_index + 1}", flush=True)
    result["medians_ms"] = {
        name: {
            phase: statistics.median(
                sample
                for row in result["rounds"]
                if row["variant"] == name
                for sample in row["phases"][phase]["samples_ms"]
            )
            for phase in ("python_api_compile", "native_compile")
        }
        for name in packages
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["medians_ms"], indent=2))


if __name__ == "__main__":
    main()
