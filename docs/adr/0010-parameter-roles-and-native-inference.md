# ADR 0010: Parameter roles and native inference initialization

Status: Accepted

## Evidence

The upstream DASH import case still failed because a `sh:Parameter` with a
`sh:node` argument annotation was compiled as an executable shape. Its UI
annotation component had no validator. A reduced offline regression reproduced
the failure for both typed and untyped parameter declarations.

The native `owl:hasKey` rule interpolated its class into SPARQL text. A blank-node
class thereby became a query variable and matched other classes, incorrectly
equating unrelated resources. Empty key lists also equated every class member,
unlike the reference. Regressions reproduced both identity errors before the fix.

Full inferred-graph tests exposed missing datatype/annotation axioms and the
three RDFS/OWL equivalences used by combined inference. RDFS resource typing also
ran every round, whereas the reference initializes it only in the first round.

## Decision

Identify parameter declarations by `sh:parameter` references and instances of
`sh:Parameter`. Argument annotations using `sh:node` or `sh:property` do not by
themselves register those declarations as validation entry points. A node can
still have two roles: an explicit shape type, target or incoming shape reference
makes it executable, with the same hard errors for unsupported validators.

Evaluate keys through native RDF term indexes. Restrict candidate subjects to
the declared class and intersect the matches for all key properties. Blank nodes
retain identity; no RDF terms are interpolated into SPARQL. Empty keys remain
inactive, matching the pinned reference. Malformed lists/property terms fail
before Python commits any inference additions.

Add one-time native datatype/annotation axioms, datatype subsumption and combined
mode bindings. Compute first-round RDFS resource typing from the initial graph
after these axioms. Retain the reference's rule distinctions for reflexive
schema entailments on declared versus undeclared classes/properties.

No Python reasoner is called and no runtime owlrl dependency is introduced.
Inference remains synchronous. Native key matching follows the full
[OWL 2 RL prp-key premises](https://www.w3.org/TR/owl2-profiles/#Reasoning_in_OWL_2_RL_and_RDF_Graphs);
the pinned Python reasoner's omission of its last key comparison is recorded as
a remaining behavioral difference rather than copied.

## Validation and limits

Regression tests cover parameter dual roles, named and blank-node key classes,
empty/multivalued/malformed keys, and success-only graph mutation. Twenty-one
complete-closure tests compare RDFS, OWL-RL and combined inference on seven
graphs covering schema statements and datatype subsumption. All pass. This is
bounded evidence, not a claim that every inference rule is complete.

The complete non-JS suite now passes 398/403 cases, with five failures retained.
Generalized triples with literal subjects remain outside the native RDF dataset
model. Legacy plain-string identity, inconsistency handling and further closure
differences remain open. Benchmark diagnostics distinguish ordinary RDF from
generalized triples without relabeling a differing full closure as equivalent.

Reasoning benchmarks must be rerun after the additional entailments. Earlier
timings remain separate artifacts identified by source hashes.
