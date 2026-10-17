# ADR 0035: Validate in the dataset-owning runtime

Status: Accepted

The companion pipeline must retain one native RDF dataset from parsing through
OWL-RL inference and SHACL validation. Independently compiled Rust Python
extensions cannot exchange Rust pointers or assume compatible Rust layouts.

rdflib-turbo therefore executes the SHACL engine inside its own native extension,
using a revision-pinned dependency on this engine's canonical source. Python
pyshacl-turbo supplies the public compatibility facade and report decoding.
Compiled shapes are immutable, reusable objects owned by the executing runtime.
No Rust object or allocation ownership crosses extension boundaries.

Expose readonly engine validation over a borrowed Dataset. It rejects active
rules and invalid options rather than copying the data. Ordinary validation
retains its rule behavior. The dataset runtime holds a read lock for readonly
validation; rule execution stages a private working dataset under its write lock
and commits only after complete success when inplace is requested. A failed
operation never changes caller data. Per-call evaluation caches cannot outlive
their lock; no cached result survives dataset mutation. Named-graph union views
remain internal and must never be committed as caller quads.

Version the Python runtime integration protocol explicitly and compare the SHA-256
fingerprint of all canonical engine implementation files before execution. The
source inventory test rejects newly added implementation files missing from the
fingerprint. Normalize CRLF transport line endings to LF, while preserving other
bytes, so Windows checkouts agree with source archives. Updating engine source requires updating the runtime's immutable
engine pin and the coordinated benchmark source pins; metadata-only package
version changes do not imply a different engine. Missing/incompatible protocols
or engine sources are hard errors, with no RDFLib or serialized-data fallback. Preserve
namespace bindings, exact RDF terms, graph scope and caller blank-node identity.
Native dataset input is an additional API; ordinary RDFLib behavior is unchanged.

The shared benchmark must exercise this actual runtime path and verify that it
cannot call dataset conversion/serialization. Keep historical conversion-based
measurements separately labeled. Release comparisons use separately locked uv
projects, exact wheel identities and identical workload/harness hashes. Compare
complete outputs before publishing performance ratios; preserve known output
differences. CI correctness and descriptive performance remain separate gates.
