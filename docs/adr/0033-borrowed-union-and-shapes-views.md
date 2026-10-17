# ADR 0033: Borrow union and shapes-graph views without base copies

Status: Accepted

SHACL validation and SPARQL constraints need a default-graph union and a temporary
named shapes graph. The existing implementation materializes those datasets.
Provide composable GraphRead views before switching complete validation to a
transaction-backed source.

UnionGraph exposes distinct triples from every source context in its default
graph, preserves original named contexts and forwards named-graph existence.
A wildcard graph match returns the union default graph plus original named facts.
Neither it nor repeated wrapping projects duplicates into the default graph.

Native memory storage traverses insertion-linked indexes, so adjacent
deduplication would be incorrect. A workspace-sized visited set would also
reintroduce the memory defect. Instead, perform an exact indexed lookup for each
candidate triple and retain only the occurrence in that lookup's first context.
A consistent source must return the same first quad for repeated identical
patterns; its iterator need not be sorted. Dataset and native transactions meet
this contract. This adds indexed lookups in exchange for constant retained state,
without reading or retaining the whole relation before yielding output. Missing
representatives and storage errors fail explicitly.

OverlayGraph reserves a fresh named graph, projects a borrowed shapes union into
it and keeps the base default/named contexts intact. Original shapes contexts do
not appear in the base. Graph existence is part of GraphRead: collisions with
empty native graphs fail too, and an empty overlay remains a named graph. The
constructor takes a NamedOrBlankNode, so a default-graph overlay is unrepresentable.
No statement is inserted into the underlying source.

These are read views, not a finished Store validation API. Complete validation,
report descriptions, query evaluation and snapshot-free function callbacks must
adopt them before that API is exposed. Existing per-path/target result collections,
reports and transaction deltas remain separate memory costs. No new storage or
wire version, side table, whole-graph snapshot or global mutable cache is added.

Canonical engine-source changes also require a coordinated rdflib-turbo consumer
pin and benchmark source revision. The wheel builder checks implementation source
differences before building; the installed-wheel fingerprint check remains strict.
Never rewrite candidate archives or relax source identity to make a mixed pair pass.
