import hashlib
import json
import statistics
import time
from pathlib import Path

import pyshacl_turbo as turbo
from rdflib import Graph, Literal, Namespace

E = Namespace("urn:term-benchmark:")
data = Graph()
for i in range(1800):
    data.add((E[f"s{i}"], E.value, Literal(i)))
shapes = Graph().parse(
    data="""@prefix sh:<http://www.w3.org/ns/shacl#> . @prefix e:<urn:term-benchmark:> .
e:S sh:targetNode e:s0; sh:rule [a sh:SPARQLRule; sh:construct "CONSTRUCT { $this e:derived true } WHERE {}"].""",
    format="turtle",
)
program = turbo.compile_shapes(shapes, advanced=True)
expected = set(data) | {(E.s0, E.derived, Literal(True))}
result = {}
for name, run in [
    ("validate", lambda: program.validate(data)),
    ("rules_full_output", lambda: program.shacl_rules(data)),
]:
    samples = []
    for i in range(8):
        start = time.perf_counter_ns()
        output = run()
        elapsed = (time.perf_counter_ns() - start) / 1e6
        if name == "validate":
            assert output[0]
        else:
            assert set(output) == expected
        assert len(data) == 1800
        if i:
            samples.append(elapsed)
    result[name] = {"samples_ms": samples, "median_ms": statistics.median(samples)}
print(
    json.dumps(
        {
            "input_triples": 1800,
            "results": result,
            "native_sha256": hashlib.sha256(Path(turbo._native.__file__).read_bytes()).hexdigest(),
        }
    )
)
