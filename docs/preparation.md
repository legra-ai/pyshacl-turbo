# Automatic SPARQL preparation

No additional call or option is needed. Repeated `validate()`, `shacl_rules()`
and `compile_shapes()` calls reuse native compilation when the current shapes
snapshot and its compilation settings match a retained entry.

The compilation key includes sorted serialized statements, RDF format, base IRI,
namespace bindings, advanced mode and the graph/document boolean interpretation
setting. The cache holds immutable native programs, not caller-owned RDFLib
graphs. Changing shapes or namespace bindings changes the key. Failed
compilations are not cached.

Blank-node identifiers are part of the snapshot identity. Independently parsed
documents can assign different identifiers and therefore miss this cache even
when their graphs are isomorphic. `compile_shapes()` remains useful when callers
want to avoid repeated shape loading, serialization and cache-key construction.
Previously compiled programs keep their existing snapshot semantics.

Inside the native evaluator, SELECT, ASK, CONSTRUCT and DESCRIBE reuse optimized
algebra keyed by the complete parsed graph pattern and the sorted set of initially
bound variable names. Including those names preserves SHACL prebinding semantics,
including `BOUND($this)`. Resolved prefixes and query literals are part of the
parsed pattern. Base-IRI execution context, dataset selection, function callbacks,
binding values and result iterators remain specific to each execution.

Each cache holds at most 128 entries and evicts the least recently used entry.
Neither cache stores query results or mutable data graphs. Graph additions and
removals are visible on the next ordinary graph call. Explicit `TargetData`
snapshots retain their separately documented immutable data and target-result
semantics. Calls an application makes directly to RDFLib's `Graph.query()` are
outside this mechanism.

The evaluator's explicit no-optimization mode bypasses the plan cache. The local
`cached-query-plans` Cargo feature enables plan reuse for Turbo; upstream-default
spareval builds keep their uncached optimizer path. Parsing, validation and
execution errors continue to propagate.

## Synthetic measurements

The local before/after comparison uses seven samples after an untimed warmup.
Shape and data construction are outside the timer. Each run checks the report,
text and unchanged input graph, and the two builds' observations agree.

| Workload | Previous top-level call, median ms | Automatic preparation, median ms |
| --- | ---: | ---: |
| One focus node, 24 SPARQL constraints | 1.353 | 0.628 |
| 256 focus nodes, one SPARQL constraint | 5.460 | 5.220 |

These measurements describe the synthetic workloads on macOS ARM64 with Python
3.13.16, not a universal speedup. Explicitly compiled calls changed only slightly
in these cases. [Raw before/after samples](../benchmarks/preparation.json) retain
the Python-source and native-binary hashes. `make benchmark-preparation` measures
the installed build and writes a fresh single-build result; run the same script
against each build to reproduce a comparison. Run with builds and tests idle.
