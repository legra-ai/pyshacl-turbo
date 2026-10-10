# ADR 0008: Native Store inputs and compiled pattern execution

Status: Accepted

## Evidence

The user requested measurements and Oxigraph/PyOxigraph dataset input. The
expanded benchmark found Core validation slower than pySHACL. For 1,000 nodes,
profiling measured about 8 ms converting input, 9 ms decoding the report and
41 ms in native parsing, validation and serialization. Removing the pattern
constraint reduced that native stage to 8 ms. Compilation created a regex but
discarded it; each value executed a general SPARQL expression instead.

## Decision

Retain compiled regexes in the immutable shape program and match lexical values
directly. Preserve flags, compile-time errors and blank-node violations. Use the
existing report comparisons and the manual Core performance regression before
and after the change. Do not put timing assertions into shared unit-test CI.

Accept PyOxigraph Store input without materializing an RDFLib data graph. Use
Store's native N-Quads snapshot and the native parser across the independently
built Python extensions. This is a copy, not a zero-copy or shared-pointer API.
Preserve named graphs and blank-node labels. Store values already normalized by
Oxigraph cannot be reconstructed to their original lexical spelling.

Rust callers can supply an oxigraph::Store directly. Copy its consistent quad
snapshot into the exact-term Dataset, without RDF serialization. For both APIs,
rule/inference additions commit atomically only after successful execution and
only when inplace is explicitly requested. Validation does not delete triples. The Python commit also computes its delta
in Rust before the Store transaction, so an unrelated concurrent deletion of
an original input quad is not undone.

PyOxigraph is an optional dependency. owlrl remains reference-test infrastructure
only. Native evaluation is synchronous, releases Python's GIL, and does not
introduce Tokio or asynchronous I/O. Parallel reuse remains caller-controlled.

## Measurement

Preserve the initial matrix in benchmarks/performance-baseline.json. Compare
RDFLib and existing Store inputs separately; include report decoding in both.
Report the cost of the Store handoff and shape compilation. Do not assign a
speedup when a reference backend errors or when validation reports differ.
Inference graph differences remain explicit, even when validation reports match.
