# ADR 0025: Reuse immutable compilation and SPARQL algebra automatically

Status: Accepted

## Evidence

Top-level Python calls reconstruct native compiled shapes on every call. Native
queries already retain parsed statements, but spareval still converts and
optimizes the graph pattern at each execution. Repeating a query over many focus
nodes therefore repeats preparation even when only data or binding values change.

ADR 0004 requires the optimizer to know which variables are initially bound.
Sharing a plan without that information changes `BOUND` and `BIND` behavior.
Dataset snapshots and callback closures cannot be shared as query results.

## Decision

Keep a process-local 128-entry LRU of native compiled programs, keyed by the exact
current shapes snapshot, namespace bindings and all native compilation settings.
Construct fresh Python wrappers and read inputs on each call. Cache no failures.
Retain blank-node identity rather than canonicalizing isomorphic shape graphs.

Build the compilation key from direct typed term batches. Native code renders,
sorts and deduplicates exact union triples into one canonical N-Triples string;
ordinary calls still inspect current graph content. Avoid Python term rendering,
graph serialization and materializing an RDFLib union graph before cache lookup.
The existing LRU key and returned shared-runtime source reference the same string;
wrappers reuse that cached source instead of retaining independent equal copies.
Keep namespace bindings and compilation settings as separate key components.
Context-only blank nodes are not part of flattened shape input. Preserve typed
literal spellings and blank labels; this is content ordering, not RDF blank-node
canonicalization. No additional cache or engine protocol is introduced.
Canonicalization streams validated quads from an owned term table rather than
building throwaway graph indexes. Ordinary direct input consumes the same
validated stream when it needs a dataset. Release the transfer batch before
native compilation so its lifetime does not overlap compilation's graph storage.

Add an opt-in `cached-query-plans` feature to the existing vendored spareval.
Enable it for the engine. Share a process-local 128-entry LRU of immutable
optimized graph patterns across all four query forms. Key on parsed algebra and
the set of initially bound variable names. These are the optimizer's inputs;
binding values, datasets, base-IRI execution context and registered callbacks are
supplied anew to the evaluator. Keep optimization enabled, and bypass the cache
when the caller explicitly requests no optimization.

Use exact structural equality for plan lookup, not a digest alone. Serialize
cache access with a mutex; poison is a hard failure. Do not intercept RDFLib's
application-level query API or introduce implicit mutable-data snapshots.

## Verification

Regressions first reproduced repeated native compilation and missing plan reuse.
Tests cover shape and prefix mutation, advanced and input settings, changed data,
failed compilation recovery, entry limits and LRU eviction. Native tests cover
different initial bindings, current callback implementations and binding values,
and fresh data for SELECT, ASK, CONSTRUCT and DESCRIBE. The standalone evaluator
suite runs with caching disabled and with Turbo's opt-in features enabled.
