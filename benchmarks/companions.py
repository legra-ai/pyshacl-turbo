"""Correctness-gated benchmarks for the three companion turbo projects.

Use the dedicated pinned environment described in companions.md. Workers import
only the backend they measure. Timing and peak RSS use separate fresh processes.
"""

import argparse
import hashlib
import json
import platform
import random
import re
import statistics
import subprocess
import sys
import time
from datetime import UTC, datetime
from importlib.metadata import distribution
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONVERSIONS = {"from_rdflib", "to_rdflib", "roundtrip"}
OPERATIONS = (
    "parse_turtle",
    "parse_nquads",
    "serialize_nt",
    "serialize_nquads",
    "select",
    "select_named",
    "ask",
    "construct",
    "rdfs",
    "owlrl",
    "from_rdflib",
    "to_rdflib",
    "roundtrip",
    "validate",
    "pipeline_rdfs",
    "pipeline_owlrl",
)
PREFIXES = """@prefix ex: <urn:example:> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
"""
SHAPES = """@prefix ex: <urn:example:> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
ex:Shape a sh:NodeShape; sh:targetClass ex:Person;
    sh:property [ sh:path ex:name; sh:minCount 1; sh:maxCount 1 ] .
"""


def fixture(nodes, *, named=False):
    """Deterministic employee records: subclass inference, joins and 10% violations."""
    schema = "ex:Employee rdfs:subClassOf ex:Person . ex:knows a owl:SymmetricProperty .\n"
    records = []
    for index in range(nodes):
        text = f'ex:p{index} a ex:Employee; ex:score "{index % 100}"^^xsd:integer; ex:knows ex:p{(index + 1) % nodes} .\n'
        if index % 10:
            text += f'ex:p{index} ex:name "Person {index}" .\n'
        records.append(text)
    if named:
        return PREFIXES + schema + "ex:records {\n" + "".join(records) + "}\n"
    return PREFIXES + schema + "".join(records)


def nquads_fixture(nodes):
    """Generate the named-graph input directly, without a parser in memory setup."""
    rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    lines = [
        "<urn:example:Employee> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <urn:example:Person> .",
        f"<urn:example:knows> <{rdf}type> <http://www.w3.org/2002/07/owl#SymmetricProperty> .",
    ]
    for index in range(nodes):
        subject = f"<urn:example:p{index}>"
        graph = "<urn:example:records>"
        lines.extend(
            [
                f"{subject} <{rdf}type> <urn:example:Employee> {graph} .",
                f'{subject} <urn:example:score> "{index % 100}"^^<http://www.w3.org/2001/XMLSchema#integer> {graph} .',
                f"{subject} <urn:example:knows> <urn:example:p{(index + 1) % nodes}> {graph} .",
            ]
        )
        if index % 10:
            lines.append(f'{subject} <urn:example:name> "Person {index}" {graph} .')
    return "\n".join(lines) + "\n"


def digest_graph(graph):
    from rdflib.compare import to_canonical_graph

    lines = sorted(" ".join(term.n3() for term in triple) for triple in to_canonical_graph(graph))
    return {"triples": len(graph), "sha256": hashlib.sha256("\n".join(lines).encode()).hexdigest()}


def graph_observation(graph):
    from rdflib import BNode, Graph, URIRef

    ordinary = Graph()
    for s, p, o in graph:
        if isinstance(s, (URIRef, BNode)) and isinstance(p, URIRef):
            ordinary.add((s, p, o))
    return {
        "ordinary": digest_graph(ordinary),
        "full": digest_graph(graph),
        "generalized_triples": len(graph) - len(ordinary),
    }


def dataset_observation(dataset):
    """Canonicalize quads together so graph scope and shared blank nodes survive."""
    from rdflib import BNode, Graph, Literal, Namespace

    quads = list(dataset.quads())
    if not any(isinstance(term, BNode) for quad in quads for term in quad):
        lines = sorted(
            json.dumps(
                [s.n3(), p.n3(), o.n3(), None if g == dataset.default_graph.identifier else g.n3()]
            )
            for s, p, o, g in quads
        )
        return {
            "quads": len(quads),
            "sha256": hashlib.sha256("\n".join(lines).encode()).hexdigest(),
        }
    encoded, predicates = Graph(), Namespace("urn:benchmark:quad:")
    for s, p, o, g in quads:
        statement = BNode()
        for predicate, term in ((predicates.s, s), (predicates.p, p), (predicates.o, o)):
            encoded.add((statement, predicate, term))
        if g == dataset.default_graph.identifier:
            encoded.add((statement, predicates.default, Literal(True)))
        else:
            encoded.add((statement, predicates.graph, g))
    return {"quads": len(quads), "structure": digest_graph(encoded)}


def rows_observation(variables, rows):
    # A sorted list preserves duplicate solutions. None retains unbound columns.
    values = [[None if value is None else value.n3() for value in row] for row in rows]
    return {"variables": [str(v) for v in variables], "rows": sorted(values, key=json.dumps)}


def catalogue(sizes):
    return [
        {
            "operation": operation,
            "nodes": nodes,
            "backends": ["turbo"] if operation in CONVERSIONS else ["reference", "turbo"],
        }
        for nodes in sizes
        for operation in OPERATIONS
    ]


def prepare(job):
    """Rebuild mutable inputs before every call, outside the measured interval."""
    import rdflib
    from rdflib import Dataset as RDFLibDataset
    from rdflib import Graph

    rdflib.NORMALIZE_LITERALS = False
    operation, backend = job["operation"], job["backend"]
    native = backend in {"turbo", "turbo_shared"}
    named = operation in {"parse_nquads", "serialize_nquads", "select_named"}
    text = fixture(job["nodes"], named=named)
    if operation == "validate" or operation.startswith("pipeline_"):
        shapes = Graph().parse(data=SHAPES, format="turtle")
    if native and operation != "validate":
        from rdflib_turbo import Dataset as NativeDataset
    if operation == "parse_nquads":
        text = nquads_fixture(job["nodes"])
    if operation.startswith("parse_"):
        fmt = "nquads" if named else "turtle"
        constructor = NativeDataset if native else RDFLibDataset
        return lambda: constructor().parse(data=text, format=fmt), lambda value: {
            "dataset": dataset_observation(value.to_rdflib() if native else value)
        }
    if operation.startswith("pipeline_"):
        mode = operation.removeprefix("pipeline_")
        if native:
            from owlrl_turbo import expand
            from pyshacl_turbo import validate

            def run():
                dataset = NativeDataset().parse(data=text)
                closure = expand(dataset, inference=mode, inplace=True)
                if backend == "turbo":
                    closure = closure.to_rdflib().default_graph
                return closure, validate(closure, shacl_graph=shapes, inference="none")
        else:
            from owlrl import DeductiveClosure, OWLRL_Semantics, RDFS_Semantics
            from pyshacl import validate

            semantics = RDFS_Semantics if mode == "rdfs" else OWLRL_Semantics

            def run():
                closure = Graph().parse(data=text, format="turtle")
                DeductiveClosure(semantics).expand(closure)
                return closure, validate(closure, shacl_graph=shapes, inference="none")

        return run, lambda value: {
            "closure": graph_observation(
                value[0].to_rdflib().default_graph if backend == "turbo_shared" else value[0]
            ),
            "report": report_observation(value[1]),
        }
    if not native or operation in CONVERSIONS or operation == "validate":
        reference = RDFLibDataset().parse(data=text, format="trig" if named else "turtle")
        graph = reference.default_graph
    if operation in CONVERSIONS:
        # No artificial reference baseline: these are costs of crossing the boundary.
        source = NativeDataset.from_rdflib(reference) if operation != "from_rdflib" else reference
        if operation == "from_rdflib":
            run = lambda: NativeDataset.from_rdflib(source)
        elif operation == "to_rdflib":
            run = source.to_rdflib
        else:
            run = lambda: NativeDataset.from_rdflib(source.to_rdflib())

        def observe(value):
            expected = dataset_observation(RDFLibDataset().parse(data=text, format="turtle"))
            actual = dataset_observation(value if operation == "to_rdflib" else value.to_rdflib())
            if actual != expected:
                raise RuntimeError("Conversion changed RDF terms or graph scope")
            return {"dataset": actual}

        return run, observe
    if operation == "validate":
        if native:
            from pyshacl_turbo import validate
        else:
            from pyshacl import validate
        # Add inferred class explicitly: validation-only must exercise all nodes.
        from rdflib import RDF, URIRef

        for index in range(job["nodes"]):
            graph.add((URIRef(f"urn:example:p{index}"), RDF.type, URIRef("urn:example:Person")))
        before = frozenset(graph)

        def observe(value):
            if frozenset(graph) != before:
                raise RuntimeError("Validation mutated the input")
            return {"report": report_observation(value)}

        return lambda: validate(graph, shacl_graph=shapes, inference="none"), observe
    source = (
        NativeDataset().parse(data=text, format="trig" if named else "turtle")
        if native
        else reference
    )
    if operation.startswith("serialize_"):
        fmt = "nquads" if named else "nt"
        target = source if native or named else graph
        return lambda: target.serialize(format=fmt), lambda value: {
            "dataset": dataset_observation(RDFLibDataset().parse(data=value, format=fmt))
        }
    if operation in {"rdfs", "owlrl"}:
        if native:
            from owlrl_turbo import expand

            run = lambda: expand(source, inference=operation)
        else:
            from owlrl import DeductiveClosure, OWLRL_Semantics, RDFS_Semantics

            semantics = RDFS_Semantics if operation == "rdfs" else OWLRL_Semantics

            def run():
                result = Graph()
                result += graph
                DeductiveClosure(semantics).expand(result)
                return result

        def observe(value):
            expected = RDFLibDataset().parse(data=text, format="turtle")
            if dataset_observation(source.to_rdflib() if native else source) != dataset_observation(
                expected
            ):
                raise RuntimeError("Inference mutated the input despite copy-by-default")
            return {
                "closure": graph_observation(value.to_rdflib().default_graph if native else value)
            }

        return run, observe
    query_body = "?person a <urn:example:Employee>; <urn:example:score> ?score; <urn:example:name> ?name . FILTER(?score >= 50)"
    queries = {
        "select": "SELECT ?person ?name WHERE { " + query_body + " }",
        "select_named": "SELECT ?person ?name WHERE { GRAPH <urn:example:records> { "
        + query_body
        + " } }",
        "ask": "ASK { <urn:example:p0> a <urn:example:Employee> }",
        "construct": "CONSTRUCT { ?s <urn:example:label> ?name } WHERE { ?s <urn:example:name> ?name }",
    }
    query = queries[operation]

    def run():
        result = source.query(query)
        if result.type == "SELECT":
            return result.vars, list(result)  # Consume RDFLib's lazy iterator inside timer.
        return bool(result) if result.type == "ASK" else result.graph

    if operation in {"select", "select_named"}:
        observe = lambda value: {"query": rows_observation(*value)}
    elif operation == "ask":
        observe = lambda value: {"query": value}
    else:
        observe = lambda value: {"query": graph_observation(value)}
    return run, observe


def report_observation(result):
    return {"conforms": result[0], "graph": digest_graph(result[1]), "text": result[2]}


def rss_bytes(value, system):
    if system == "darwin":
        return value
    if system == "linux":
        return value * 1024
    raise RuntimeError("Peak RSS measurement requires Linux or macOS")


def without_report_text(observation):
    result = dict(observation)
    if "report" in result:
        result["report"] = {k: v for k, v in result["report"].items() if k != "text"}
    return result


def worker(job, repeats, measurement):
    import resource

    samples, observations = [], []
    iterations = repeats + 1 if measurement == "time" else 1
    for index in range(iterations):
        run, observe = prepare(job)
        before = rss_bytes(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, sys.platform)
        start = time.perf_counter_ns()
        value = run()
        elapsed = time.perf_counter_ns() - start
        peak = rss_bytes(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, sys.platform)
        observation = observe(value)
        if observations and without_report_text(observation) != without_report_text(
            observations[0]
        ):
            raise RuntimeError("Repeated RDF observations are unstable")
        observations.append(observation)
        if measurement == "time" and index:
            samples.append(elapsed)
        del value, run, observe
    return {
        "observation": observations[0],
        "observations": observations,
        "stable": all(value == observations[0] for value in observations),
        "samples_ns": samples,
        "peak_rss_bytes": peak,
        "setup_peak_rss_bytes": before,
    }


def compare(reference, turbo, reference_ns, turbo_ns):
    if reference == turbo:
        return {"status": "equal", "speedup": reference_ns / turbo_ns}
    # Preserve the complete observations and withhold full-output speedups even
    # when only the intentionally excluded generalized statements differ.
    if "closure" in reference and "closure" in turbo:
        left, right = dict(reference), dict(turbo)
        left["closure"] = reference["closure"]["ordinary"]
        right["closure"] = turbo["closure"]["ordinary"]
        if left == right:
            return {"status": "standard_rdf_equal", "speedup": None}
    if "report" in reference and "report" in turbo:
        left, right = dict(reference), dict(turbo)
        for value in (left, right):
            value["report"] = {k: v for k, v in value["report"].items() if k != "text"}
            if "closure" in value:
                value["closure"] = value["closure"]["ordinary"]
        if left == right:
            return {"status": "report_graph_equal", "speedup": None}
    return {"status": "different", "speedup": None}


def comparison_for_runs(reference, turbo):
    if not reference["stable"] or not turbo["stable"]:
        return {
            "status": "unstable",
            "speedup": None,
            "first_observation_comparison": compare(
                reference["observation"], turbo["observation"], 1, 1
            ),
        }
    return compare(
        reference["observation"], turbo["observation"], reference["median_ns"], turbo["median_ns"]
    )


def launch(job, repeats, measurement, timeout):
    sys.path.insert(0, str(ROOT / "tests"))
    from upstream_support.process_launch import Popen

    command = [
        sys.executable,
        "-I",
        str(Path(__file__).resolve()),
        "--worker",
        json.dumps(job),
        "--repeats",
        str(repeats),
        "--measurement",
        measurement,
    ]
    with Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise RuntimeError(f"Worker timeout after {timeout}s: {job}") from None
        if process.returncode:
            raise RuntimeError(f"Worker failed ({process.returncode}): {job}\n{stderr}")
    return json.loads(stdout)


def measure(job, repeats, memory_repeats, timeout):
    timed = launch(job, repeats, "time", timeout)
    memory = [launch(job, repeats, "memory", timeout) for _ in range(memory_repeats)]
    if any(
        without_report_text(sample["observation"]) != without_report_text(timed["observation"])
        for sample in memory
    ):
        raise RuntimeError(f"Cold memory and warm timing RDF observations differ: {job}")
    stable = timed["stable"] and all(
        sample["observation"] == timed["observation"] for sample in memory
    )
    return {
        "observation": timed["observation"],
        "observations": timed["observations"],
        "stable": stable,
        "samples_ns": timed["samples_ns"],
        "median_ns": statistics.median(timed["samples_ns"]),
        "memory_samples": [
            {k: sample[k] for k in ("peak_rss_bytes", "setup_peak_rss_bytes", "observation")}
            for sample in memory
        ],
        "median_peak_rss_bytes": statistics.median(sample["peak_rss_bytes"] for sample in memory),
    }


def environment():
    packages = {}
    pins = dict(
        re.findall(
            r"^([a-z0-9-]+)==([^\s]+)",
            (ROOT / "benchmarks/companions-requirements.lock").read_text(),
            re.MULTILINE,
        )
    )
    for name, pin in pins.items():
        dist = distribution(name)
        if dist.version != pin or dist.read_text("direct_url.json"):
            raise RuntimeError(
                f"{name} must use the pinned PyPI artifact {pin}; use the dedicated benchmark environment"
            )
        packages[name] = {"version": dist.version, "direct_url": dist.read_text("direct_url.json")}
        packages[name]["native_sha256"] = {
            str(path): hashlib.sha256(dist.locate_file(path).read_bytes()).hexdigest()
            for path in dist.files
            if str(path).endswith((".so", ".pyd", ".dylib"))
        }
    files = [
        Path(__file__),
        ROOT / "benchmarks/companions-requirements.lock",
        ROOT / "benchmarks/uv.lock",
        ROOT / "benchmarks/pyproject.toml",
        ROOT / "tests/upstream_support/process_launch.py",
    ]
    return {
        "date": datetime.now(UTC).isoformat(),
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": packages,
        "source_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files
        },
    }


def write_report(result, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# Companion turbo project benchmarks",
        "",
        result["method"],
        "",
        f"Measured {result['environment']['date']}; {result['environment']['platform']}.",
        "",
        "| Operation | Nodes | Reference ms | Turbo ms | Full-output speedup | Parity | Reference peak MiB | Turbo peak MiB |",
        "|---|---:|---:|---:|---:|---|---:|---:|",
    ]
    for run in result["runs"]:
        ref, native = run["backends"].get("reference"), run["backends"].get("turbo")

        def cell(backend, key, divisor):
            return f"{backend[key] / divisor:.3f}" if backend else "—"

        speedup = run.get("comparison", {}).get("speedup")
        status = run.get("comparison", {}).get("status", "diagnostic")
        lines.append(
            f"| {run['operation']} | {run['nodes']} | {cell(ref, 'median_ns', 1e6)} | {cell(native, 'median_ns', 1e6)} | {f'{speedup:.2f}×' if speedup is not None else '—'} | {status} | {cell(ref, 'median_peak_rss_bytes', 2**20)} | {cell(native, 'median_peak_rss_bytes', 2**20)} |"
        )
    lines += [
        "",
        "Raw samples, complete observations, package versions and source hashes are in the adjacent JSON file.",
        "These deterministic synthetic workloads do not establish complete compatibility or predict application performance.",
        "",
    ]
    output.with_suffix(".md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", type=int, nargs="+", default=[100, 1000])
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--memory-repeats", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--operations", choices=OPERATIONS, nargs="+", default=list(OPERATIONS))
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks/companions-current.json")
    parser.add_argument("--worker", help=argparse.SUPPRESS)
    parser.add_argument(
        "--measurement", choices=["time", "memory"], default="time", help=argparse.SUPPRESS
    )
    args = parser.parse_args()
    if min(args.nodes) < 1 or min(args.repeats, args.memory_repeats) < 1 or args.timeout <= 0:
        parser.error("sizes, repetitions and timeout must be positive")
    rss_bytes(0, sys.platform)
    if args.worker:
        print(json.dumps(worker(json.loads(args.worker), args.repeats, args.measurement)))
        return
    result = {
        "environment": environment(),
        "repeats": args.repeats,
        "memory_repeats": args.memory_repeats,
        "method": "Serial isolated workers. One warmup then retained timing samples; inputs rebuilt outside timers. Pipeline includes data parsing, inference, RDFLib conversion and complete validation output; shapes prepared outside timer. Separate cold workers measure whole-process peak RSS immediately after one operation, before observation encoding, including interpreter, backend imports, fixtures and retained output. Setup high-water marks are recorded, not subtracted. No process startup, file I/O or correctness hashing in timings. Generalized reference triples remain visible; full-output speedups require every observation to agree. Phase times are independent and must not be summed. Conversions are unpaired diagnostics. No timing thresholds.",
        "runs": [],
    }
    rng = random.Random(20261016)
    try:
        for job in catalogue(args.nodes):
            if job["operation"] not in args.operations:
                continue
            row = {"operation": job["operation"], "nodes": job["nodes"], "backends": {}}
            result["runs"].append(row)
            order = list(job["backends"])
            rng.shuffle(order)
            for backend in order:
                row["backends"][backend] = measure(
                    {"operation": job["operation"], "nodes": job["nodes"], "backend": backend},
                    args.repeats,
                    args.memory_repeats,
                    args.timeout,
                )
            if "reference" in row["backends"]:
                ref, native = row["backends"]["reference"], row["backends"]["turbo"]
                row["comparison"] = comparison_for_runs(ref, native)
            print(
                f"{job['operation']} ({job['nodes']} nodes): {row.get('comparison', {}).get('status', 'diagnostic')}",
                flush=True,
            )
    except Exception as error:
        result["error"] = str(error)
        write_report(result, args.output)
        raise
    write_report(result, args.output)


if __name__ == "__main__":
    main()
