# ADR 0009: Native advanced features and auditable compatibility measurements

Status: Accepted

## Evidence

The complete pinned suite exposed missing TripleRules, SHACL functions, node
expressions, custom target types, ontology inoculation, Meta-SHACL and CLI I/O.
The existing report used random blank-node labels, making its text unstable.
Two upstream tests asserted a reference Python callback and wrapper class,
neither of which exists in the native architecture.

## Decision

Implement TripleRules, node expressions (this, constants, paths, union,
intersection, filterShape and function calls), ASK/SELECT functions, and
parameterized SPARQL target types in Rust. Functions register per evaluation,
with independent data snapshots and bounded recursion. Callback errors propagate
through lazy SPARQL result iteration; they cannot disappear into an empty result
and a conforming report. No Python evaluator executes.

Continue compiling ordinary queries once. Queries that call SHACL functions
currently prepare against an evaluation-specific function registry. That path
has additional snapshot and preparation costs which must remain measurable.

Ontology inoculation copies schema statements and explicit NamedIndividuals,
without importing unrelated instance data. Native inference still has known
closure differences from owlrl. Meta-SHACL uses the packaged, attributed shapes
asset and the same native validator. CLI and DASH helpers adapt I/O and expected
results only. Native code constructs validation reports and stable term
representations, with namespace bindings supplied by the Python boundary.

Add an opt-in parser API for externally supplied projection variables. SHACL
prebindings remain legal across aggregate subqueries without relaxing ordinary
SPARQL parsing. Keep the change in the vendored spargebra patch, with a regression.

Disable upstream failure allowances for both engines. Run the same 403 non-JS
cases. Record original IDs for the two implementation-coupled tests together with
explicit native-equivalent names. One verifies the Store adapter and blank-node
identity; the other selects only the SPARQL constraint and verifies the two
violations that require native custom-function invocation. Never run the
reference callback or fabricate its invocation to satisfy a spy.

Shape discovery follows explicit types, targets and shape-expecting predicates.
Parameter annotations alone do not make executable shapes. Validate and cache
standalone path syntax without registering metadata as shapes. Imported Core
component declarations use their native implementation and are not registered
again as custom components requiring a SPARQL validator.

Report verbatim passes, native equivalents and reference failures separately.
Passing a finite test suite is not proof of universal feature compatibility.
The fail-fast recursion policy from ADR 0002 was retained at this checkpoint.
The user subsequently authorized reference recursion and undefined-function
semantics in [ADR 0012](0012-reference-recursion-and-expression-errors.md).
Registered callback execution errors still propagate.
