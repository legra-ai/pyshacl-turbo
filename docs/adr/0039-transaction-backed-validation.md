# ADR 0039: Borrow the transaction throughout SHACL execution

Status: Accepted

Supersedes phase snapshots in ADR 0026 and named-graph working copies in ADR 0028.
Use GraphRead throughout targets, constraints, functions, display and reports.
UnionGraph supplies the logical default graph; OverlayGraph supplies shapes
separately. Scoped evaluator functions borrow the same phase source, while
explicit evaluator registrations retain precedence. Storage failures remain
errors throughout lazy query iteration and report construction.

CompiledShapes.validate_transaction runs rules directly on pending native writes
and never commits. The caller owns acceptance and transaction finalization.
validate_staged and validate_delta borrow the source and retain only new rule
quads. expand_store now returns additions rather than a full dataset. Dataset
consumers serialize the report before extending their base with the delta.

The shared Python facade accepts native Dataset, Store and Transaction through
source-owned adapters. Report decoding and warning emission occur inside the
adapter's context, allowing Store/Transaction owners to abort on consumer errors.
The Store commit gate owns conformance policy; direct validation returns reports.
Keep shared protocol 1 and require exact engine-source fingerprints; do not
serialize native sources or load a second storage extension to bridge versions.

Avoiding base snapshots does not bound target sets, per-rule results, validation
reports or SPARQL intermediates. This decision does not claim constant-memory
validation of arbitrary SHACL programs.
