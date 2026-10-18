# ADR 0037: Evaluate SPARQL against borrowed logical graph views

Status: Accepted

Expose QueryGraph as the QueryableDataset adapter for GraphRead. Query evaluation
borrows the same consistent source as native traversal, including pending native
transaction changes. Explicitly compose UnionGraph and OverlayGraph before
querying; the adapter must never union the shapes overlay into the default graph.

SPARQL wildcard graph matching means named graphs only, whereas GraphRead's absent
graph filter includes the default graph. Translate that distinction explicitly.
Invalid RDF term kinds in subject, predicate or graph patterns yield no matches.
Retain exact RDF terms and forward iterator and graph-metadata errors.

GraphRead pattern references are temporary inputs, not part of the read lifetime.
Dataset reads retain at most four owned pattern terms and choose an indexed
candidate stream. Native transactions encode patterns before returning iterators.
Views forward those streams without extending caller-owned pattern borrows.

Require streaming named-graph enumeration as well as existence checks. Native
transactions expose their metadata, including empty graphs. OverlayGraph appends
its reserved graph even when empty, and UnionGraph forwards source metadata.
Dataset has no empty graph metadata: select one indexed representative quad per
named graph, without a dataset-sized graph-name set. This adds indexed probes
rather than retaining all graph names or modifying the vendored dataset API.

This adapter is a prerequisite, not a Store validation API. Full validation and
snapshot-free SHACL function callbacks still need adoption. The SPARQL evaluator's
query-dependent join, sort, aggregate and output costs remain separate; the adapter
itself introduces no whole-base snapshot or materialized graph-name collection.
Canonical engine changes require coordinated consumer and benchmark source pins,
as required by ADR 0033. No storage, wire or integration-protocol version changes.

The README and crate rustdoc share a static, accessible SVG shipped with source
archives. Crate documentation embeds the SVG and a tested transaction example,
without a JavaScript renderer. Native coverage CI also builds warning-free public
rustdoc at the requested revision and retains it as an artifact. The existing
green-main GitHub Pages publication installs that artifact under `/rustdoc/`;
package publication remains solely in the tested release pipeline.
