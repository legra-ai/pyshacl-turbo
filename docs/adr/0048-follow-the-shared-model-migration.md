# ADR 0048: Follow the provider's move onto the shared model crates

Status: Proposed; design only, see rdflib-turbo ADR 0079

The SHACL engine and its bindings live in rdflib-turbo (`crates/engine`,
`crates/python`; rdflib-turbo ADR 0068). rdflib-turbo ADR 0079 proposes
that the compiler use shacl-structural-model types directly instead of the
parallel engine structures it lowers them into today, that report terms
become rdf-structural-model terms, that the engine's duplicate CONSTRUCT
reasoner be replaced by the provider's reasoner, and that SHACL 1.2
inference rules be lowered to datalog-structural-model. SHACL-AF rules keep
pySHACL's ordering and iteration semantics in the engine. See
[rdflib-turbo ADR 0079](https://github.com/legra-ai/rdflib-turbo/blob/main/docs/adr/0079-move-internals-onto-shared-model-crates.md).

Adopt that record's slices and gates for this package. Every slice must keep
the corrected pySHACL suite at 403/403 and reconcile the SHACL 1.0, SHACL 1.2,
upstream and direct-contract outcomes exactly with `tests/divergences.toml`
(ADR 0047), with no new entry. Reference input quirks reproduced on purpose
(ADR 0007, ADR 0021) stay in the compiler and must still reconcile.

Order the planned pyshacl-turbo work around it: the small-input fixed-cost
work comes before the compiler slice and supplies its baseline; typed
validation limits follow the reasoner consolidation; the total result order
and canonical report gate follow RDF dataset canonicalization and ship with
the compiler slice. The Python facade and its public API do not change.
