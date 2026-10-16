import hashlib
import json
import statistics
import time
from pathlib import Path

import pyshacl_turbo as turbo
from pyshacl_turbo import rdf
from rdflib import BNode, Graph, Literal, Namespace
from rdflib.namespace import SH

E = Namespace("urn:traversal-benchmark:")
results = {}
for kind in ["repeated_complex_path", "single_predicate_path"]:
    data, shapes = Graph(), Graph()
    if kind == "repeated_complex_path":
        path = BNode()
        shapes.add((path, SH.oneOrMorePath, E.next))
        for i in range(300):
            data.add((E[f"n{i}"], E.next, E[f"n{i + 1}"]))
        for i in range(24):
            s = E[f"S{i}"]
            shapes.add((s, SH.targetNode, E.n0))
            shapes.add((s, SH.path, path))
            shapes.add((s, SH.minCount, Literal(1)))
    else:
        for i in range(500):
            data.add((E[f"n{i}"], E.value, Literal(i)))
        shapes.add((E.S, SH.targetSubjectsOf, E.value))
        shapes.add((E.S, SH.path, E.value))
        shapes.add((E.S, SH.minCount, Literal(1)))
    program = turbo.compile_shapes(shapes)
    source = rdf.input_graph(data)
    samples = []
    for i in range(8):
        start = time.perf_counter_ns()
        output = program.validate(source)
        elapsed = (time.perf_counter_ns() - start) / 1e6
        assert output[0]
        if i:
            samples.append(elapsed)
    results[kind] = {
        "input_triples": len(data),
        "samples_ms": samples,
        "median_ms": statistics.median(samples),
    }
print(
    json.dumps(
        {
            "results": results,
            "native_sha256": hashlib.sha256(Path(turbo._native.__file__).read_bytes()).hexdigest(),
        }
    )
)
