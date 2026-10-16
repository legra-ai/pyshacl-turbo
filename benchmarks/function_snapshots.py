import hashlib, json, statistics, time
from pathlib import Path
import pyshacl_turbo as t
from rdflib import Graph, Namespace, Literal

E = Namespace("urn:function-bench:")
g = Graph()
for i in range(1600):
    g.add((E[f"n{i}"], E.value, Literal(i)))
for i in range(120):
    g.add((E[f"n{i}"], E.target, Literal(True)))
s = Graph().parse(
    data="""@prefix sh:<http://www.w3.org/ns/shacl#> . @prefix e:<urn:function-bench:> .
e:f a sh:SPARQLFunction; sh:select "SELECT (1 AS ?result) WHERE {}".
e:S sh:targetSubjectsOf e:target; sh:sparql [sh:select "SELECT $this WHERE { FILTER(e:f() != 1) }"].""",
    format="turtle",
)
p = t.compile_shapes(s, advanced=True)
samples = []
for i in range(8):
    start = time.perf_counter_ns()
    result = p.validate(g)
    ms = (time.perf_counter_ns() - start) / 1e6
    assert result[0] and len(g) == 1720
    if i:
        samples.append(ms)
print(
    json.dumps(
        {
            "input_triples": len(g),
            "focus_nodes": 120,
            "samples_ms": samples,
            "median_ms": statistics.median(samples),
            "native_sha256": hashlib.sha256(Path(t._native.__file__).read_bytes()).hexdigest(),
        }
    )
)
