# ADR 0004: Make SPARQL optimization aware of initial bindings

Status: Accepted

## Evidence

W3C pre-binding-003, -004 and -005 fail with Oxigraph 0.5.11: the optimizer
simplifies BOUND($this) as false, or drops a BIND expression, before the evaluator
receives the initial bindings. A native regression reproduces this for both an
IRI and a blank-node focus. An outer SELECT projection alone does not supply
bindings through nested projections.

## Decision

Vendor sparopt 0.3.7 and spareval 0.2.7 from the exact published crate sources.
Add an optimizer entry point with initial bound-variable types, and call it from
spareval's four query forms using the substitutions already provided by its API.
Keep optimization enabled. Preserve the existing no-bindings optimizer API.
Expose SHACL's auxiliary bindings through the compiled query's projection scopes.

Translate $PATH in the parsed SPARQL algebra, only in predicate position. Traverse
expressions as well as graph patterns when checking forbidden constructs. MINUS,
SERVICE, VALUES, rebinding prebound variables and subqueries that do not project
$this produce a dedicated ValidationFailure, a Python ValueError subclass. This
project raises validation failures instead of returning pySHACL's failure object.

## Consequences

The patches are explicit local dependencies with provenance in vendor/README.md.
They need upstream review before removal; no upstream contribution has been sent.
Run the native prebinding regression, W3C prebinding cases and existing rule tests
when upgrading either crate. No unoptimized or Python evaluation fallback exists.
