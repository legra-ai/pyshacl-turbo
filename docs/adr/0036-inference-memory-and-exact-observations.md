# ADR 0036: Measure inference memory and retain exact output checks at larger sizes

Status: Accepted

The dataset-owning runtime's ADR 0005 replaces full inference snapshots with an
additive insertion journal and distinct-new-fact buffers. Pin that implementation
in the coordinated wheel suite. Keep before/after source and wheel identities,
every timing/RSS sample and every complete observation. Development package
versions alone do not identify candidate binaries.

Separate requested native Rust heap from whole-process RSS. The runtime's opt-in
release test binary profiles parse, inference, shape compilation and native
validation/report serialization. Counters do not measure Python allocations,
allocator arenas or facade report decoding. They diagnose phases, not additive
estimates of end-to-end performance. Installed uninstrumented wheels remain the
source of public-operation timing and cold-process peak RSS. Atomic rollback,
inferred closures and complete reports must remain correct.

At larger sizes, RDFLib's general blank-node refinement can dominate correctness
encoding even for uniquely anchored validation results. Retain full comparisons
with a canonical bijection when every blank node has a unique label-independent
local signature. Signatures encode every position, self-reference, nonblank term
and anonymous neighbor marker; output encoding then retains every complete triple
under that bijection. Isomorphic graphs choose the same method and labels. Equal
encoded triple sets still require an isomorphism, subject to the same cryptographic
hash assumption as ordinary digests. Local signatures alone are never compared
as a substitute for complete graph structure.

Ambiguous graphs retain RDFLib's general canonicalizer. Selection is based on
structural ambiguity before comparison; a failed comparison never retries with
a weaker observation. Tests cover renaming, shared versus duplicated nodes,
disconnected facts, symmetric cycles with different global connectivity, self
loops and generalized blank-node predicates. Raw digests name the encoder, and
harness hashes identify the implementation. Do not equate hashes from different
encoder versions across historical reports.

The historical companion catalogue explicitly selects the `rdflib-v1` encoder
in its Make target and CI. Keep that exact wire format and its original immutable
baseline. New release workers explicitly select `unique-anchors-v1`. A per-worker
context prevents encoder selection from leaking between calls; unknown versions
and conflicting declarations fail before execution. This is upfront version
selection, never a retry after comparison failure.

Keep all observation encoding after the operation timer and RSS capture, as ADR
0031 requires. Every repeat still retains complete observations. The weekly
10,000-record workload has a larger explicit per-worker time budget; worker
errors/timeouts remain hard failures and cannot publish successful history.
