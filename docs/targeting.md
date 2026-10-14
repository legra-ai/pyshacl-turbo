# Reusable data snapshots for focus-node discovery

`prepare_target_data(data_graph)` creates an immutable native snapshot for
repeated `Shape.focus_nodes()` calls. Reuse the snapshot and `ShapesGraph` to
serialize and parse the data once and cache target sets for subsequent calls.

```python
from rdflib import Graph
from pyshacl_turbo import ShapesGraph, prepare_target_data

data = Graph().parse(data='''
    @prefix ex: <urn:example:> .
    ex:alice a ex:Person .
''', format="turtle")
shape_definitions = Graph().parse(data='''
    @prefix ex: <urn:example:> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    ex:People a sh:NodeShape; sh:targetClass ex:Person .
''', format="turtle")

shapes = ShapesGraph(shape_definitions)
snapshot = prepare_target_data(data)
shape = next(iter(shapes.shapes))
shape.set_advanced(True)  # Include SHACL-AF targets when present.

first = shape.focus_nodes(snapshot)   # Evaluate and cache this shape's targets.
again = shape.focus_nodes(snapshot)   # Read the cached targets.
assert first == again
```

The snapshot shares its parsed native dataset across shapes. Target sets are
cached separately for each compiled shape program, shape identity and advanced
mode setting. Every call returns a separate Python set, so modifying a returned
set does not change cached results. Named graphs, blank-node identities and
explicit literal datatypes are preserved.

## Data changes

A snapshot represents the data at preparation time. Prepare a new snapshot
when additions or removals should become visible:

```python
from rdflib import RDF, URIRef

data.add((URIRef("urn:example:bob"), RDF.type, URIRef("urn:example:Person")))
snapshot = prepare_target_data(data)
updated = shape.focus_nodes(snapshot)
assert URIRef("urn:example:bob") in updated
```

Reuse one snapshot for repeated reads of unchanged data. Passing an ordinary
graph to `shape.focus_nodes(data)` reads fresh data each time and pays conversion
costs each time. Snapshot preparation is explicit; graphs are not implicitly
cached by identity. Preparing an existing `TargetData` returns the same snapshot.

## Which shapes target a node?

`CompiledShapes.targeting(data, node, skip=())` returns the identifiers of active
node shapes whose declared targets include the supplied RDFLib term. Results
are a fresh list sorted by the identifiers' N3 spelling. Property shapes and
deactivated shapes are excluded. Shapes reached only through constraints such
as `sh:node` or `sh:property` are not declared targets.

```python
from rdflib import URIRef
from pyshacl_turbo import compile_shapes

program = compile_shapes(shape_definitions, advanced=True)
matches = program.targeting(snapshot, URIRef("urn:example:alice"))
assert matches == [URIRef("urn:example:People")]
assert program.targeting(
    snapshot, URIRef("urn:example:alice"), skip={URIRef("urn:example:People")}
) == []
```

The data argument accepts an ordinary input or a prepared `TargetData` snapshot.
An ordinary input is freshly loaded on each call. A snapshot builds a native
reverse index once per compiled program and exclusion set, then reuses it across
lookups for different nodes. `ShapesGraph.targeting(data, node, skip=())` exposes
the same operation when using the inspection API.

`node` must be an RDFLib `URIRef`, `BNode`, or `Literal`. `skip` must be an
iterable of shape `URIRef` or `BNode` identifiers. Skipped shapes are not evaluated,
and target errors propagate without caching an incomplete index. Supported
SHACL-AF targets require `advanced=True` when compiling the shapes. Parameterized
SPARQL target types and SPARQL result ordering and limits are preserved.

The operation discovers declared targets; it does not run validation, rules,
or inference. Explicit literal and absent-node targets can match even when
the target term is not present in the data graph. No validation report is needed.

## Measured example

The synthetic benchmark uses ten shapes and 1,000 data nodes. Values below are
median milliseconds for a complete pass over all ten shapes, using five samples
after an untimed warmup. Fixture construction and shape compilation are outside
the timer; every timed target set is checked against pySHACL.

| Target kind | pySHACL | Turbo, ordinary graph | Turbo, fresh snapshot including preparation | Turbo, reused snapshot |
| --- | ---: | ---: | ---: | ---: |
| Core class | 4.487 | 196.451 | 164.510 | 0.059 |
| SPARQL | 74.319 | 201.575 | 167.767 | 0.052 |

The fresh-snapshot column includes preparation and first evaluation. The reused
column reads already cached target sets. Reuse removes repeated conversion and
evaluation costs; the first pass still has those costs and can be slower than
pySHACL. These measurements describe the synthetic fixture, not all workloads.

Recorded environment: macOS ARM64, Python 3.13.16, RDFLib 7.6.0, pySHACL 0.40.1,
and a local Turbo release build. [Raw samples](../benchmarks/targeting.json)
include source and native-module hashes. Reproduce with builds and tests idle:

```sh
make benchmark-targeting
```
