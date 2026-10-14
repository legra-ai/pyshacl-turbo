"""Measure live versus explicitly snapshotted focus-node calls after parity checks.

Run with builds and tests idle. Shape compilation and fixture construction are
outside the timer. Fresh-snapshot samples include preparing and reading the
snapshot; reused-snapshot samples follow one untimed complete pass. Every timed
result must equal the reference, and every sample is retained.
"""

import argparse
import hashlib
import json
import platform
import statistics
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from time import perf_counter_ns

import pyshacl_turbo as turbo
from pyshacl.shapes_graph import ShapesGraph as ReferenceShapesGraph
from rdflib import RDF, Graph, Literal, Namespace
from rdflib.namespace import SH

ROOT = Path(__file__).resolve().parents[1]
EX = Namespace("urn:target-bench:")


def measure(run, expected, repeats):
    samples = []
    for _ in range(repeats):
        start = perf_counter_ns()
        result = run()
        elapsed = (perf_counter_ns() - start) / 1_000_000
        if result != expected:
            raise AssertionError("Target sets differ; refusing performance comparison")
        samples.append(elapsed)
    return {"samples_ms": samples, "median_ms": statistics.median(samples)}


def benchmark(nodes, count, repeats, advanced):
    data, shapes = Graph(), Graph()
    expected_nodes = {EX[f"node{i}"] for i in range(nodes)}
    for node in expected_nodes:
        data.add((node, RDF.type, EX.Person))
    for i in range(count):
        node = EX[f"Shape{i}"]
        shapes.add((node, RDF.type, SH.NodeShape))
        if advanced:
            target = EX[f"Target{i}"]
            shapes.add((node, SH.target, target))
            shapes.add((target, RDF.type, SH.SPARQLTarget))
            shapes.add(
                (
                    target,
                    SH.select,
                    Literal(f"SELECT ?this WHERE {{ ?this <{RDF.type}> <{EX.Person}> }}"),
                )
            )
        else:
            shapes.add((node, SH.targetClass, EX.Person))
    reference = sorted(ReferenceShapesGraph(shapes).shapes, key=lambda shape: str(shape.node))
    replacement = sorted(turbo.ShapesGraph(shapes).shapes, key=lambda shape: str(shape.node))
    for shape in reference + replacement:
        shape.set_advanced(advanced)
    expected = {shape.node: expected_nodes for shape in reference}

    def focus(items, source):
        return {shape.node: shape.focus_nodes(source) for shape in items}

    prepared = turbo.prepare_target_data(data)
    runners = {
        "reference": lambda: focus(reference, data),
        "turbo_live_graph": lambda: focus(replacement, data),
        "turbo_fresh_snapshot_including_preparation": lambda: focus(
            replacement, turbo.prepare_target_data(data)
        ),
        "turbo_reused_snapshot": lambda: focus(replacement, prepared),
    }
    for run in runners.values():
        if run() != expected:
            raise AssertionError("Warmup target sets differ")
    results = {name: measure(run, expected, repeats) for name, run in runners.items()}
    return {
        "targets": "sparql" if advanced else "core_class",
        "data_triples": len(data),
        "shape_count": count,
        "focus_nodes_per_shape": nodes,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", type=int, default=1000)
    parser.add_argument("--shapes", type=int, default=10)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if min(args.nodes, args.shapes, args.repeats) < 1:
        parser.error("nodes, shapes, and repeats must be positive")
    sources = [ROOT / "Cargo.toml", ROOT / "Cargo.lock", ROOT / "pyproject.toml", Path(__file__)]
    for directory, patterns in (
        ("crates", ("*.rs", "Cargo.toml")),
        ("vendor", ("*.rs", "Cargo.toml")),
        ("python", ("*.py",)),
    ):
        for pattern in patterns:
            sources.extend((ROOT / directory).rglob(pattern))
    digest = hashlib.sha256()
    for path in sorted(sources):
        digest.update(str(path.relative_to(ROOT)).encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    from pyshacl_turbo import _native

    report = {
        "measured_at": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "versions": {name: version(name) for name in ("pyshacl", "pyshacl-turbo", "rdflib")},
        "source_sha256": digest.hexdigest(),
        "native_sha256": hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),
        "repeats": args.repeats,
        "workloads": [benchmark(args.nodes, args.shapes, args.repeats, af) for af in (False, True)],
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    for workload in report["workloads"]:
        print(
            workload["targets"],
            {name: round(result["median_ms"], 3) for name, result in workload["results"].items()},
        )


if __name__ == "__main__":
    main()
