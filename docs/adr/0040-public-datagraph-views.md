# ADR 0040: Live RDFLib DataGraph views

Status: Accepted

Expose DataGraph and RdfLibDataGraph from graph_abstraction as prerequisites for
the public validation and rule runner classes. RDFLib Graph and Dataset views
retain the caller's store, graph identifiers, namespace manager and mutations.
They are adapters, not snapshots or alternate SHACL interpreters.

Match the reference factory, default-union, locked-context, query-binding and
clone contracts. Clones write directly into their final independent destination,
preserving graph scopes and default graph identifiers. Native input preparation
unwraps the adapter's implementation graph so a plain Graph sharing a larger
context-aware store cannot accidentally expose unrelated contexts.

RDFLib graph queries retain their RDFLib backend. SHACL validation, rule expansion
and inference remain in the native engine; importing the reference validator is
never an execution fallback. Graphs owned by another native Store runtime fail
before conversion or copying. Shared Store graph adapters and optional
PyOxigraph-backed DataGraph construction remain separate parity work.

The public `shacl_rules` function returns the same DataGraph view protocol for
RDFLib object inputs as for document inputs. Iteration yields quads. In-place
results share the caller's store; independent results clone the selected view
once and apply the native insertion delta to that destination. Preserve custom
default identifiers and declared empty contexts instead of rebuilding a flat
Graph from the rule closure. ConjunctiveGraph term transfer uses its actual
default context and the identifiers of its Graph-valued quad contexts.
