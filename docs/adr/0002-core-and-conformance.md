# ADR 0002: Expand coverage with pinned standards and compatibility inventories

Status: Accepted; recursion policy superseded by [ADR 0012](0012-reference-recursion-and-expression-errors.md)

## Context

ADR 0001 established the native execution boundary and a deliberately small first
milestone. The next authorized work expands Core constraints, property paths,
SHACL-SPARQL and advanced features. The first milestone's feature limit is no
longer the implementation target; its test-first and no-fallback requirements remain.

## Decision

- Vendor the complete W3C test tree and the pySHACL 0.40.1 test assets at immutable
  revisions. Record passes, mismatches, unsupported features and harness failures
  separately. An unsupported test is never a conformance pass.
- Implement shape composition and property paths as native Rust structures. Use
  RDF term identity and cycle-safe traversal for paths; reject malformed lists.
- Retain complete RDF reports for differential testing, including nested details.
  Standard reports may omit generated messages and optional details; apply only
  the normalization prescribed by the test contract and document it.
- Keep Rust responsible for value semantics, evaluation and report generation.
  Do not call Python validators or use Python evaluation as a fallback.
- Recursive shape conformance is not defined by SHACL 1.0. This ADR originally
  required an explicit error. ADR 0012 supersedes that policy with the user's
  authorized pySHACL recursion compatibility behavior.
- Keep unsupported features visible while subsequent work implements them.

## Consequences

Core support is measured against all pinned Core fixtures rather than a selected
passing subset. pySHACL compatibility and W3C conformance remain separate claims;
differences must be described and reproduced before choosing behavior.
