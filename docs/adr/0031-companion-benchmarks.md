# ADR 0031: Measure the companion projects at their public boundaries

Status: Accepted

The first rdflib-turbo and owlrl-turbo alphas share one native dataset runtime.
pyshacl-turbo currently receives an explicit RDFLib copy. Before integrating their
dataset ownership, establish a reproducible public-API baseline that exposes this
conversion cost. These three companion projects have no platform affiliation.

Keep the canonical suite in `benchmarks/companions.py`, linked by all three
repositories. Pin published wheels and transitive dependencies with hashes in a
dedicated environment. Record versions, native binary hashes and harness hashes.
Do not silently import local sibling builds or replace a failing backend.

Measure parsing, serialization, materialized queries, RDFS/OWL-RL inference,
validation, both conversion directions and complete pipelines. Time public
operations on equivalent inputs; exclude fixture setup and correctness encoding.
Copy-by-default inference includes its copy. The complete pipeline starts at RDF
text and includes the current conversion and public report output. Separate phase
times are diagnostics, never additive estimates. Conversion phases have no
artificial reference baseline.

Use serial, time-bounded fresh workers and ADR 0006's macOS spawn launcher.
Separate timing workers (one warmup plus retained samples) from cold memory
workers (one operation, captured before observation encoding). Peak RSS includes
the interpreter, imports, fixture setup and output; record the setup high-water
mark without claiming that subtracting high-water marks isolates operation memory.
This harness explicitly supports Linux and macOS memory units.

Respect ADRs 0020 and 0021: compare full RDF structure and report text, retain raw
generalized-RDF differences, and publish full-output speedups only for stable,
completely equal observations. A known boundary or text difference remains a
difference. Preserve every sample's observations when output is unstable; such
rows earn no ratio. Worker errors and invalid conversions must fail, with partial
evidence retained. Keep CI correctness checks separate from noisy timing numbers.

These synthetic records cover the current alpha public APIs. They establish
neither complete replacement compatibility nor a universal performance claim.
