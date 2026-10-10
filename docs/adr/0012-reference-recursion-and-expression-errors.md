# ADR 0012: Match reference recursion and undefined-function behavior

Status: Accepted; supersedes the recursive-shape error policy in ADR 0002

## Context

The user explicitly resolved the conflict between fail-fast execution and exact
pySHACL compatibility in favor of the reference behavior for recursive shapes
and undefined SPARQL functions. The policy does not permit hiding errors raised
by registered SHACL function implementations.

## Decision

Track shape/constraint pairs along the validation path. Match pySHACL 0.40.1's
recursion trigger: three pairs, or six for alternating Node/Property constraints.
Node, Property, Not and QualifiedValueShape constraints warn and skip a recursive
edge. Continue evaluating the shape's other constraints. Focus-node equality is
not the trigger. Preserve nested reports and empty-value shortcuts, including
the qualified constraint's disjoint flag when its sibling set is empty.

Allow cyclic property-shape references at compilation. Enforce the reference
validation depth limit, default 15 and configurable with max_validation_depth.
And/Or/Xone recursion has no warn-and-skip exception and fails at that limit.

Return recursion diagnostics from the Rust validation and rule APIs. Python
emits ShapeRecursionWarning, a ValidationWarning/RuntimeWarning subclass, before
committing additions to caller-owned Graphs or Stores. A warnings-as-errors
policy therefore prevents mutation. The direct Rust APIs return the warnings
as data; they do not depend on Python warning filters.

Enable a narrowly scoped spareval feature that evaluates unknown scalar
functions as expression errors. FILTER, BIND, COALESCE and logical operators
apply their normal SPARQL expression-error semantics. Default vendored behavior
remains unchanged without that feature. Errors from registered native SHACL
callbacks still propagate through lazy result iteration as required by ADR 0009.

## Evidence and limits

Differential regressions cover direct and indirect recursion, changing focus
nodes, alternating constraints, nested violations, negation, qualified counts,
rule conditions, depth limits and atomic mutation with warnings as errors.
Unknown-function tests cover FILTER, BIND, COALESCE, UNION and short-circuiting.
The existing registered-function arity-error regression remains a hard failure.

The strict non-JS suite now passes 402/403 cases, including two documented native
equivalents. Its one remaining failure is the audited incorrect assertion in
bad_test_070; it remains failed. No denominator or upstream fixture was changed.
This finite suite does not establish universal compatibility. These recursion
semantics are a pySHACL compatibility choice, not a SHACL conformance claim.
