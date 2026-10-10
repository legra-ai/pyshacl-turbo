# ADR 0011: Preserve literal identity and report graph context

Status: Accepted

## Evidence

Upstream issue 286 and reduced differential tests distinguish a plain string
from an explicit xsd:string in RDFLib. The previous oxrdf constructors collapsed
both before validation. This lost values, changed cardinality and affected
Core comparisons, rule output and inferred datatype axioms.

Preserving these terms exposed a separate DASH checker defect: the reference
compares expected literals by value, whereas Turbo tested exact triple membership.
Its Store rule output was correct, but this comparison rejected it.

The blank-node report discrepancy was previously attributed to a stale reference
cache. Instrumentation disproved that diagnosis. pySHACL places dataset inference
in `urn:pyshacl:inference` and describes a blank node from a source graph. Turbo
placed additions in the default graph and described the synthetic union.

## Decision

Enable an opt-in oxrdf feature which retains plain and explicit xsd:string
variants through constructors, Dataset interning, parsing and serialization.
Use the original datatype IRI; do not encode a private datatype or special-case
an individual constraint. Exact Core comparisons and SPARQL sameTerm retain
identity; SPARQL value equality continues to compare values. Without the feature,
the vendored crate retains upstream RDF 1.1 string identity.

Restore explicit xsd:string at the Store input boundary, matching the reference
Store adapter. Store dump abbreviations must not silently change that adapter's
term identity. Caller-side Store canonicalization remains irreversible.

Use value equality for literal objects in DASH inference expectations. This
changes only the expected-result adapter; validation retains exact RDF terms.

Python Graph input keeps inference in its graph. Dataset, document and Store
inputs place new inferred statements in `urn:pyshacl:inference`, preserving
original contexts. Rust exposes `infer_into` for an explicit destination.
Descriptions select a source context before inference; nested blank descriptions
stay in that context. Validation and RDF report cloning still use all evaluated
statements, including inference. No mutable description cache is introduced.

## Validation and limits

Regressions reproduce term loss before the change and cover Core identity,
cardinality, SPARQL identity/value equality, rules, four document formats and
both Store string forms. Other tests cover DASH literal value comparisons,
Graph/document/Dataset descriptions and inplace inference destinations. Existing
tests asserting default-graph inference were corrected against the reference.

At this checkpoint, the complete strict non-JS suite passed 400/403, including the two explicitly
recorded native equivalents. Recursion and undefined functions retain hard
errors pending resolution of the user's fail-fast/compatibility requirements.
That policy is subsequently resolved in [ADR 0012](0012-reference-recursion-and-expression-errors.md).
The third failure is an incorrect assertion also present in the reference;
an immutable-fixture audit confirms equivalent nonconforming RDF reports.
Its missing class message is reproduced by a separate offline regression.
The strict test remains failed and the denominator remains 403.

Benchmarks now fingerprint dependency sources and Cargo manifests/lockfile as
well as application code. Older benchmark artifacts predate this patch and must
not be presented as current measurements. Passing these finite suites does not
prove complete pySHACL behavior, inference closure or report-text equivalence.
