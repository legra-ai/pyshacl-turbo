"""Reproducible synthetic pipeline benchmark; every backend must match first."""

import argparse
import json
import platform
import statistics
import time
from importlib.metadata import version
from pathlib import Path

import pyoxigraph
import pyshacl
import pyshacl_turbo as turbo
from rdflib import RDF, Graph, Literal, Namespace
from rdflib.compare import isomorphic

EX = Namespace("https://example.com/")
ROOT = Path(__file__).resolve().parents[1]


def benchmark(count, repeats):
    data = Graph()
    for index in range(count):
        node = EX[f"person{index}"]
        data.add((node, RDF.type, EX.Person))
        data.add((node, EX.enabled, Literal(True)))
        if index % 2 == 0:
            data.add((node, EX.email, Literal(f"person{index}@example.com")))
    shapes = Graph().parse(ROOT / "tests/fixtures/pipeline-shapes.ttl")
    compiled = turbo.compile_shapes(shapes, advanced=True)

    def reference_oxigraph():
        store = pyoxigraph.Store()
        store.load(input=data.serialize(format="nt"), format=pyoxigraph.RdfFormat.N_TRIPLES)
        return pyshacl.validate(store, shacl_graph=shapes, advanced=True)

    runners = {
        "pyshacl_rdflib": lambda: pyshacl.validate(data, shacl_graph=shapes, advanced=True),
        "pyshacl_oxigraph": reference_oxigraph,
        "turbo": lambda: turbo.validate(data, shacl_graph=shapes, advanced=True),
        "turbo_reused_shapes": lambda: compiled.validate(data),
    }
    reference = runners["pyshacl_rdflib"]()
    for name, run in runners.items():
        actual = run()
        if actual[0] != reference[0] or not isomorphic(actual[1], reference[1]):
            raise AssertionError(f"Report mismatch for {name}; refusing performance comparison")

    samples = {name: [] for name in runners}
    for _ in range(repeats):
        for name, run in runners.items():
            start = time.perf_counter_ns()
            run()
            samples[name].append((time.perf_counter_ns() - start) / 1_000_000)
    return {
        "focus_nodes": count,
        "input_triples": len(data),
        "results": len(
            list(reference[1].objects(None, Namespace("http://www.w3.org/ns/shacl#").result))
        ),
        "median_ms": {
            name: round(statistics.median(values), 3) for name, values in samples.items()
        },
        "samples_ms": samples,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", type=int, nargs="+", default=[100, 1000])
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repeats < 1 or any(n < 1 for n in args.nodes):
        parser.error("nodes and repeats must be positive")
    result = {
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pyshacl": version("pyshacl"),
            "pyoxigraph": version("pyoxigraph"),
        },
        "method": "Median of warmed calls, RDFLib Graph input and report output. Oxigraph baseline includes Graph serialization and loading. Reused-shapes excludes initial shape compilation. No process startup or file I/O in timings. Synthetic SPARQL-rule pipeline, not the screenshot workload.",
        "runs": [],
    }
    for count in args.nodes:
        run = benchmark(count, args.repeats)
        result["runs"].append(run)
        print(json.dumps(run), flush=True)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
