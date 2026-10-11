# ADR 0021: Keep inference output within standard RDF

Status: Accepted

## Context

The owner explicitly rejected literal subjects in inference output. The pinned
reference reasoner leaves generalized triples in some expanded RDFLib graphs,
for example a literal typed as `rdfs:Resource`. Copying those statements would
make ordinary RDF serialization and Store input fail.

[RDF 1.1 triples](https://www.w3.org/TR/rdf11-concepts/#section-triples) have an
IRI or blank node as subject and an IRI as predicate. The specification describes
[generalized RDF](https://www.w3.org/TR/rdf11-concepts/#section-generalized-rdf)
separately as an extension useful in reasoning. That does not make generalized
statements members of an ordinary RDF graph.

## Decision

Public validation, rule and inference output must remain standard RDF. Do not
emit triples with literal subjects or non-IRI predicates. Literal objects remain
unchanged. Do not introduce a compatibility mode that exposes generalized triples
merely to copy the reference reasoner's output.

This confirms the native dataset boundary in ADR 0010 and resolves ADR 0020's
open compatibility-mode question for generalized triples. It does not excuse
missing valid RDF entailments or change the separate key-matching decision.
Internal reasoning techniques may differ as long as they preserve the required
valid RDF consequences and public behavior.

Keep raw reference observations and full-output comparisons intact. Report
generalized reference statements separately from comparisons of valid RDF.
A difference caused only by reference generalized output is an intentional
contract boundary, not unfinished support for literal subjects. It still must
not be counted as byte-for-byte or complete reference-output equality. Valid RDF
differences remain compatibility work; no filtering may hide them.

## Verification

Regressions cover RDFS, OWL-RL and combined inference on literal-valued data.
They require the fixture to expose generalized reference output, compare all
ordinary RDF entailments, retain the original literal objects and verify an
N-Triples round trip. The benchmark comparison separately records generalized
statement counts and rejects differences in the ordinary RDF portion.
