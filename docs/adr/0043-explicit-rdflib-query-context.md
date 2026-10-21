# ADR 0043: Preserve RDFLib query context in shared SPARQL evaluation

Status: Accepted

RDFLib initial bindings are an execution context, not strict substitution of
projected result variables. They can affect hidden variables and nested SELECTs,
while unused parameters must not enlarge result projections. BIND replacement,
OPTIONAL retry, VALUES rows and EXISTS grouping depend on original query scope
and order. Applying ordinary optimizer equivalences to this context changes
results.

The shared parser and evaluator expose an explicit RDFLib context mode. Preserve
source projection metadata separately from execution projection variables inside
EXISTS, and lower original algebra boundaries before optimizing individual BGP
leaves. The explicit unoptimized entry disables that leaf optimization as well.
Ordinary parsing, strict substitution and default evaluator planning retain their
existing semantics. Initial context and callbacks remain execution-owned; no
prepared plan captures prior binding values, mutable sources or callback state.

Both engine visitors traverse the source-scope projection exactly as ordinary
Project: constraint validation inspects aggregate/expression variables and adds
required prebound execution variables; regex lowering visits nested expressions.
Original source projection metadata is retained. Reject unsupported query forms
through the existing validation errors rather than skipping a new algebra node.

The canonical query patch contains the owning runtime's query-specific evaluator,
parser and optimizer changes. Preserve the canonical source's existing feature
profile, storage representation, custom-function callbacks and CONSTRUCT
implementation. A runtime-specific Oxigraph convenience wrapper is not another
engine implementation and stays in that runtime. Updating a consumer pin must
select these actual shared source bytes and the matching facade; strict engine
fingerprints remain required. Internal integration protocol remains 1.

DELETE/INSERT WHERE uses the same ordered lowering. Its private update
projection includes initial globals absent from WHERE; template lookup first
consults the explicit solution and then the immutable initial context for keys
hidden by nested projection. This never adds hidden keys to SELECT row domains.
Each operation starts with the original context, so local BIND replacements do
not leak into later semicolon-separated operations. Ordinary SPARQL remains
unchanged and INSERT DATA does not consult initial bindings.
