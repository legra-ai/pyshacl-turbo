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
