"""Measure repeated public calls with synthetic SPARQL shapes and fresh execution."""

import argparse
import hashlib
import json
import platform
import statistics
from pathlib import Path
from time import perf_counter_ns

import pyshacl_turbo as turbo
from rdflib import RDF, Graph, Literal, Namespace
from rdflib.compare import to_isomorphic
from rdflib.namespace import SH

EX = Namespace("urn:preparation-benchmark:")


def workload(nodes, constraints, repeats):
    data, shapes = Graph(), Graph()
    shapes.add((EX.Shape, SH.targetClass, EX.Record))
    for index in range(nodes):
        node = EX[f"node{index}"]
        data.add((node, RDF.type, EX.Record))
        data.add((node, EX.value, Literal(index)))
    for index in range(constraints):
        constraint = EX[f"constraint{index}"]
        shapes.add((EX.Shape, SH.sparql, constraint))
        shapes.add(
            (
                constraint,
                SH.select,
                Literal(
                    f"SELECT $this WHERE {{ $this <{EX.value}> ?v . FILTER(?v < {-index - 1}) }}"
                ),
            )
        )
    program = turbo.compile_shapes(shapes)
    original = set(data)
    expected = None
    results = {}
    for name, run in {
        "top_level": lambda: turbo.validate(data, shacl_graph=shapes),
        "explicit_compiled": lambda: program.validate(data),
    }.items():
        samples = []
        for repeat in range(repeats + 1):
            start = perf_counter_ns()
            conforms, report, text = run()
            elapsed = (perf_counter_ns() - start) / 1_000_000
            observation = (conforms, to_isomorphic(report).graph_digest(), text)
            if expected is None:
                expected = observation
            if observation != expected or not conforms or set(data) != original:
                raise AssertionError("Public observations changed; refusing timing comparison")
            if repeat:
                samples.append(elapsed)
        results[name] = {"samples_ms": samples, "median_ms": statistics.median(samples)}
    return {
        "data_triples": len(data),
        "focus_nodes": nodes,
        "constraints": constraints,
        "observation": expected,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("repeats must be positive")
    result = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "version": turbo.__version__,
        "source_hashes": {
            str(path.name): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(turbo.__file__), Path(turbo._native.__file__))
        },
        "cases": [workload(1, 24, args.repeats), workload(256, 1, args.repeats)],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
