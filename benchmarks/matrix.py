"""Correctness-gated, warmed, end-to-end and phase benchmarks. Run serially."""

import argparse
import hashlib
import json
import platform
import random
import re
import statistics
import time
from collections import Counter
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

import pyoxigraph
import pyshacl
import pyshacl_turbo as turbo
from rdflib import BNode, Graph, Literal, Namespace
from rdflib.compare import isomorphic
from rdflib.namespace import OWL, RDF, RDFS, SH, XSD

EX = Namespace("https://example.com/")
ROOT = Path(__file__).resolve().parents[1]


def native_provenance():
    """Identify the actual native artifact; do not invent local provider sources."""
    from rdflib_turbo import _native as provider

    fingerprint = provider.SHACL_ENGINE_FINGERPRINT
    if (
        not re.fullmatch(r"[0-9a-f]{64}", fingerprint)
        or turbo._native.SHACL_ENGINE_FINGERPRINT != fingerprint
        or turbo._native.CompiledShapes is not provider.shacl.CompiledShapes
    ):
        raise RuntimeError("Benchmark facade uses a different native engine")
    module = Path(provider.__file__).resolve(strict=True)
    if module.suffix not in (".so", ".pyd", ".dylib", ".dll"):
        raise RuntimeError("Benchmark provider must be the actual compiled native module")
    return {
        "version": version("rdflib-turbo"),
        "module": str(module),
        "module_sha256": hashlib.sha256(module.read_bytes()).hexdigest(),
        "engine_fingerprint": fingerprint,
    }


def make_case(kind, nodes, shape_count=1):
    data, shapes = Graph(), Graph()
    for g in (data, shapes):
        g.bind("ex", EX)
        g.bind("sh", SH)
    # The Store adapter exposes xsd:string explicitly. Use identical terms in
    # both inputs when a SPARQL report includes the original string as sh:value.
    email_datatype = XSD.string if kind == "sparql-patterns" else None
    for i in range(nodes):
        node = EX[f"person{i}"]
        data.add((node, RDF.type, EX.Employee if kind == "rdfs" else EX.Person))
        data.add((node, EX.enabled, Literal(True)))
        if i % 10:
            data.add((node, EX.email, Literal(f"person{i}@example.com", datatype=email_datatype)))
        elif kind == "sparql-patterns":
            data.add((node, EX.email, Literal(f"person{i}@invalid", datatype=email_datatype)))
    if kind == "rdfs":
        data.add((EX.Employee, RDFS.subClassOf, EX.Person))
        data.add((EX.email, RDFS.domain, EX.Person))
    elif kind == "owlrl":
        data.add((EX.Person, OWL.equivalentClass, EX.Eligible))
    if kind == "rules":
        shapes.parse(ROOT / "tests/fixtures/pipeline-shapes.ttl")
    elif kind == "sparql-patterns":
        shapes.add((EX.Shape, RDF.type, SH.NodeShape))
        shapes.add((EX.Shape, SH.targetClass, EX.Person))
        shapes.add((EX.Shape, SH.sparql, EX.PatternConstraint))
        shapes.add((EX.PatternConstraint, SH.message, Literal("A valid email is required")))
        shapes.add(
            (
                EX.PatternConstraint,
                SH.select,
                Literal(
                    f"SELECT $this ?value WHERE {{ $this <{EX.email}> ?value . "
                    'FILTER(!REGEX(?value, "^person[0-9]+@example[.]com$") || '
                    'REPLACE(?value, "^([^@]+)@.*$", "$1") != '
                    f'STRAFTER(STR($this), "{EX}")) }}'
                ),
            )
        )
    else:
        for i in range(shape_count):
            shape, prop = EX[f"Shape{i}"], EX[f"Property{i}"]
            shapes.add((shape, RDF.type, SH.NodeShape))
            if kind == "shapes":
                shapes.add((shape, SH.targetNode, EX[f"person{i % nodes}"]))
            else:
                shapes.add((shape, SH.targetClass, EX.Eligible if kind == "owlrl" else EX.Person))
            shapes.add((shape, SH.property, prop))
            shapes.add((prop, SH.path, EX.email))
            shapes.add((prop, SH.minCount, Literal(1)))
            shapes.add((prop, SH.datatype, XSD.string))
            shapes.add((prop, SH.pattern, Literal("^[^@]+@[^@]+[.][^@]+$")))
            shapes.add((prop, SH.message, Literal("A valid email is required")))
    return {
        "name": f"{kind}-{nodes}-nodes-{shape_count}-shapes",
        "kind": kind,
        "nodes": nodes,
        "shape_count": shape_count,
        "data": data,
        "shapes": shapes,
        "options": {
            "advanced": kind == "rules",
            "inference": kind if kind in {"rdfs", "owlrl"} else "none",
        },
    }


def flat_report(graph):
    """Exact linear comparison for reports whose only blank nodes are results.

    All triples must be accounted for. Complex paths/descriptions/details use
    general RDF isomorphism instead. Counters preserve duplicate result nodes.
    """
    roots = list(graph.subjects(RDF.type, SH.ValidationReport))
    if len(roots) != 1 or not isinstance(roots[0], BNode):
        return None
    root = roots[0]
    metadata = frozenset((p, o) for p, o in graph.predicate_objects(root) if p != SH.result)
    if any(isinstance(o, BNode) for _, o in metadata):
        return None
    results = Counter()
    counted = len(metadata)
    for result in graph.objects(root, SH.result):
        if not isinstance(result, BNode) or result == root:
            return None
        properties = frozenset(graph.predicate_objects(result))
        if any(isinstance(o, BNode) for _, o in properties):
            return None
        results[properties] += 1
        counted += len(properties) + 1
    return (metadata, results) if counted == len(graph) else None


def same_graph(left, right):
    a, b = flat_report(left), flat_report(right)
    return a == b if a is not None and b is not None else isomorphic(left, right)


def compare_inferred_graphs(reference, native):
    ordinary = []
    generalized = []
    for source in (reference, native):
        graph = Graph()
        count = 0
        for s, p, o in source:
            if isinstance(s, Literal) or isinstance(p, (BNode, Literal)):
                count += 1
            else:
                graph.add((s, p, o))
        ordinary.append(graph)
        generalized.append(count)
    return {
        "pyshacl_triples": len(reference),
        "turbo_triples": len(native),
        "graphs_isomorphic": isomorphic(reference, native),
        "ordinary_rdf_graphs_isomorphic": isomorphic(*ordinary),
        "pyshacl_generalized_triples": generalized[0],
        "turbo_generalized_triples": generalized[1],
    }


def require_same_report(expected, actual, name):
    if (
        actual[0] != expected[0]
        or not isinstance(actual[1], Graph)
        or not same_graph(actual[1], expected[1])
    ):
        raise AssertionError(f"{name}: report mismatch; refusing to report a speedup")


def time_calls(runners, repeats):
    # Interleave and rotate order reproducibly to reduce cache/thermal order bias.
    samples = {name: [] for name in runners}
    rng = random.Random(20261010)
    for _ in range(repeats):
        names = list(runners)
        rng.shuffle(names)
        for name in names:
            start = time.perf_counter_ns()
            result = runners[name]()
            elapsed = (time.perf_counter_ns() - start) / 1_000_000
            samples[name].append(elapsed)
            del result
    return {
        name: {
            "median_ms": statistics.median(values),
            "min_ms": min(values),
            "max_ms": max(values),
            "samples_ms": values,
        }
        for name, values in samples.items()
    }


def benchmark(case, repeats):
    data, shapes, options = case["data"], case["shapes"], case["options"]
    compiled = turbo.compile_shapes(shapes, advanced=options["advanced"])
    store = pyoxigraph.Store()
    store.load(input=data.serialize(format="nt"), format=pyoxigraph.RdfFormat.N_TRIPLES)

    def reused():
        prepared = turbo._prepare_data(data, None, None, None, options["inference"], False)
        return compiled.validate(prepared)

    def reused_store():
        prepared = turbo._prepare_data(store, None, None, None, options["inference"], False)
        return compiled.validate(prepared)

    runners = {
        "pyshacl": lambda: pyshacl.validate(data, shacl_graph=shapes, **options),
        "turbo": lambda: turbo.validate(data, shacl_graph=shapes, **options),
        "turbo_reused_shapes": reused,
        "pyshacl_oxigraph": lambda: pyshacl.validate(store, shacl_graph=shapes, **options),
        "turbo_oxigraph": lambda: turbo.validate(store, shacl_graph=shapes, **options),
        "turbo_oxigraph_reused_shapes": reused_store,
    }
    expected = runners["pyshacl"]()
    unavailable = {}
    for name, runner in list(runners.items()):
        try:
            actual = runner()
        except TypeError as error:
            if (
                name != "pyshacl_oxigraph"
                or "subject" not in str(error)
                or "Literal" not in str(error)
            ):
                raise
            unavailable[name] = f"{type(error).__name__}: {error}"
            del runners[name]
            print(f"Reference Store reasoning failed: {error}", flush=True)
            continue
        require_same_report(expected, actual, name)
    if len(store) != len(data):
        raise AssertionError("A validation backend mutated the input store")
    print(f"Reports match: {case['name']}", flush=True)
    measurements = time_calls(runners, repeats)

    data_text, shapes_text = data.serialize(format="turtle"), shapes.serialize(format="turtle")
    phases = {
        "pyshacl_load_data": lambda: Graph().parse(data=data_text, format="turtle"),
        "turbo_load_data": lambda: turbo.load_from_source(data_text, rdf_format="turtle"),
        "pyshacl_load_shapes": lambda: Graph().parse(data=shapes_text, format="turtle"),
        "turbo_load_shapes": lambda: turbo.load_from_source(shapes_text, rdf_format="turtle"),
        "turbo_compile_shapes": lambda: turbo.compile_shapes(shapes, advanced=options["advanced"]),
        "oxigraph_store_handoff": lambda: turbo._input(store),
    }
    inference = None
    if options["inference"] != "none":
        from pyshacl.graph_abstraction import DataGraph
        from pyshacl.run_type import PySHACLRunType

        def reference_reasoning():
            graph = Graph()
            graph += data
            PySHACLRunType._run_pre_inference(
                DataGraph.from_rdflib_graph(graph), options["inference"]
            )
            return graph

        def turbo_reasoning():
            return turbo._prepare_data(data, None, None, None, options["inference"], False)

        reference_inferred, turbo_inferred = reference_reasoning(), turbo_reasoning()
        inference = compare_inferred_graphs(reference_inferred, turbo_inferred)
        phases["pyshacl_reasoning_including_copy"] = reference_reasoning
        phases["turbo_reasoning_including_copy_and_conversion"] = turbo_reasoning
        phases["pyshacl_validation_after_reasoning"] = lambda: pyshacl.validate(
            reference_inferred, shacl_graph=shapes
        )
        phases["turbo_validation_after_reasoning_reused_shapes"] = lambda: compiled.validate(
            turbo_inferred
        )
    for runner in phases.values():
        runner()
    phase_times = time_calls(phases, repeats)
    return {
        **{k: case[k] for k in ("name", "kind", "nodes", "shape_count", "options")},
        "data_triples": len(data),
        "shape_triples": len(shapes),
        "result_count": len(list(expected[1].objects(None, SH.result))),
        "reports_isomorphic": True,
        "measurements": measurements,
        "unavailable_backends": unavailable,
        "phases": phase_times,
        "inference_graphs": inference,
        "speedup": measurements["pyshacl"]["median_ms"] / measurements["turbo"]["median_ms"],
        "reused_speedup": measurements["pyshacl"]["median_ms"]
        / measurements["turbo_reused_shapes"]["median_ms"],
    }


def write_report(result, output):
    output.write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# Performance comparison",
        "",
        f"Measured {result['environment']['date']}; {result['environment']['platform']}; Python {result['environment']['python']}.",
        "",
        "Warm median milliseconds. RDFLib graph input and complete RDFLib report output; Turbo includes compilation and all conversions. Reused shapes exclude compilation but still include inference. Process startup, fixture construction and file I/O are excluded. Every timed workload first passed complete report-graph isomorphism against pySHACL. These are synthetic cases.",
        "",
        f"{result['repeats']} interleaved samples per configuration; raw samples and source hashes are in [{output.name}]({output.name}). A larger speedup is better. Measurements are descriptive, not a confidence interval.",
        "",
        "| Workload | Data triples | Shape triples | Results | pySHACL ms | Turbo ms | Reused ms | Speedup | Reused speedup |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    if note := result["environment"].get("load_note"):
        lines[8:8] = [f"Load note: {note}", ""]
    for r in result["runs"]:
        m = r["measurements"]
        lines.append(
            f"| {r['name']} | {r['data_triples']:,} | {r['shape_triples']:,} | {r['result_count']:,} | {m['pyshacl']['median_ms']:.2f} | {m['turbo']['median_ms']:.2f} | {m['turbo_reused_shapes']['median_ms']:.2f} | {r['speedup']:.2f}× | {r['reused_speedup']:.2f}× |"
        )
    lines += [
        "",
        "## Loading, compilation and reasoning",
        "",
        "Independent phase timings are diagnostic and must not be summed into the end-to-end figures. Reference loading uses RDFLib's Turtle parser. Turbo loading includes its Rust parser and conversion to RDFLib. Inference timings include a fresh copy of the data.",
        "",
    ]
    lines[
        lines.index("## Loading, compilation and reasoning") : lines.index(
            "## Loading, compilation and reasoning"
        )
    ] = [
        "## Existing PyOxigraph Store input",
        "",
        "Both engines receive an already loaded Store. Initial Store loading is excluded; the Python-to-Rust handoff, validation and RDFLib report construction are included. Turbo's handoff uses native N-Quads serialization and parsing; it avoids an intermediate RDFLib data graph but is not zero-copy.",
        "",
        "| Workload | pySHACL ms | Turbo ms | Turbo reused ms | Store-to-store speedup |",
        "|---|---:|---:|---:|---:|",
        *[store_row(r) for r in result["runs"]],
        "",
        "A dash means pySHACL's Store reasoning failed on a literal subject; the exact exception is recorded in JSON. No speedup is assigned to an unavailable backend.",
        "",
    ]
    for r in result["runs"]:
        lines += [f"### {r['name']}", "", "| Phase | Median ms |", "|---|---:|"]
        lines += [f"| {name} | {values['median_ms']:.2f} |" for name, values in r["phases"].items()]
        if r["inference_graphs"]:
            inf = r["inference_graphs"]
            lines += [
                "",
                f"Inferred graphs: pySHACL {inf['pyshacl_triples']:,} triples; Turbo {inf['turbo_triples']:,}. Entire inferred graphs isomorphic: **{inf['graphs_isomorphic']}**.",
                f"Generalized triples (literal subjects or non-IRI predicates): pySHACL {inf['pyshacl_generalized_triples']:,}; Turbo {inf['turbo_generalized_triples']:,}. Ordinary RDF portions isomorphic: **{inf['ordinary_rdf_graphs_isomorphic']}**. This diagnostic does not replace the full-graph comparison.",
            ]
            if not inf["graphs_isomorphic"]:
                lines += [
                    "Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup."
                ]
        lines.append("")
    lines += [
        "Compatibility remains incomplete; this benchmark only certifies the displayed workloads. Native OWL-RL coverage is still being expanded. No result here establishes 100% pySHACL compatibility."
    ]
    output.with_suffix(".md").write_text("\n".join(lines) + "\n")


def store_row(row):
    times = row["measurements"]
    turbo_ms = times["turbo_oxigraph"]["median_ms"]
    reused_ms = times["turbo_oxigraph_reused_shapes"]["median_ms"]
    reference = times.get("pyshacl_oxigraph")
    reference_ms = f"{reference['median_ms']:.2f}" if reference else "—"
    speedup = f"{reference['median_ms'] / turbo_ms:.2f}×" if reference else "—"
    return f"| {row['name']} | {reference_ms} | {turbo_ms:.2f} | {reused_ms:.2f} | {speedup} |"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--load-note", help="Record known concurrent load or measurement limits")
    parser.add_argument(
        "--kinds",
        nargs="+",
        choices=["core", "shapes", "rules", "rdfs", "owlrl", "sparql-patterns"],
    )
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks/performance.json")
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("repeats must be positive")
    cases = [
        ("core", 100, 1),
        ("core", 1000, 1),
        ("core", 10000, 1),
        ("sparql-patterns", 100, 1),
        ("sparql-patterns", 1000, 1),
        ("shapes", 1000, 10),
        ("shapes", 1000, 100),
        ("shapes", 1000, 1000),
        ("rules", 100, 1),
        ("rules", 1000, 1),
        ("rules", 5000, 1),
        ("rdfs", 100, 1),
        ("rdfs", 1000, 1),
        ("owlrl", 100, 1),
        ("owlrl", 1000, 1),
    ]
    if args.quick:
        cases = [
            ("core", 10, 1),
            ("sparql-patterns", 10, 1),
            ("shapes", 10, 10),
            ("rules", 10, 1),
            ("rdfs", 10, 1),
            ("owlrl", 10, 1),
        ]
    if args.kinds:
        cases = [c for c in cases if c[0] in args.kinds]
    native = native_provenance()
    sources = list((ROOT / "python").rglob("*.py")) + [
        ROOT / "pyproject.toml",
        ROOT / "uv.lock",
        Path(__file__),
    ]
    result = {
        "environment": {
            "date": datetime.now(UTC).isoformat(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "pyshacl": version("pyshacl"),
            "rdflib": version("rdflib"),
            "owlrl_reference_only": version("owlrl"),
            "turbo": version("pyshacl-turbo"),
            "pyoxigraph": version("pyoxigraph"),
            "load_note": args.load_note,
        },
        "source_sha256": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(sources)
        },
        "native_artifact": native,
        "performance_eligible": False,
        "repeats": args.repeats,
        "runs": [],
    }
    for specification in cases:
        row = benchmark(make_case(*specification), args.repeats)
        result["runs"].append(row)
        write_report(result, args.output)
        print(
            f"{row['name']}: {row['speedup']:.2f}x; reused {row['reused_speedup']:.2f}x", flush=True
        )


if __name__ == "__main__":
    main()
