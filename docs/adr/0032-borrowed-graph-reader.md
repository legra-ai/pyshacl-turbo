# ADR 0032: Borrow indexed graph reads from datasets and transactions

Status: Accepted

The shared rdflib-turbo Store now supports exact-term storage and native scoped
transactions. SHACL cannot adopt that storage by materializing a Store snapshot:
that retains the whole-dataset memory cost the transaction design removes.

Introduce GraphRead as the engine's fallible, borrowed indexed-read boundary.
Implement it for oxrdf Dataset and Oxigraph Transaction. Match explicit graph
contexts: None means every graph; DefaultGraph means only the default graph.
Do not implicitly project a graph union, deduplicate all stored statements or
clone base indexes. Owned output terms live only as long as the caller retains
them. Storage failures propagate through traversal, never become missing values.
The source storage must preserve exact terms; this reader cannot recover lexical
information already lost by an upstream Store encoding.

Move existing graph lookups, class-instance traversal and property-path evaluation
to this boundary. Dataset callers retain their existing behavior. Transaction
reads see preceding insertions/deletions while committed Store readers remain
isolated. Tests also exercise abort and read failures from another implementation.

This is a prerequisite, not a new Store validation API. Compilation, complete
validation and SHACL rule execution still use Dataset. Remaining work includes
streamed union views, report descriptions, graph overlays for $shapesGraph and
SPARQL function evaluation without whole-dataset callback snapshots. No Store
validation entry point may use a copied Dataset as a substitute for those steps.

The reader itself streams. Existing per-node path result sets, class traversal,
validation reports and transaction deltas can still scale with their results;
this change is not a bounded-memory validation guarantee. It does not change
ADR 0003's exact-term requirement or certify standards/profile completeness.
