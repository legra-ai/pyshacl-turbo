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
