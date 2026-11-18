# ADR 0047: Grade the W3C SHACL 1.2 suite and keep one divergence ledger

Status: Accepted

## Evidence

Known differences from pySHACL were recorded in four places: a strict `xfail`
in `tests/test_w3c.py`, the direct-contract baseline JSON, the upstream
reference report and ADR prose. None of them failed when a recorded difference
disappeared, so stale records accumulated; `docs/direct-contract.md` still named
Turbo 0.1.0 and pySHACL 0.40.1 long after both had changed. The locally patched
upstream `bad_test_070` fixture was counted in the same pass total as the
unmodified vendored cases. Nothing measured the W3C SHACL 1.2 test suite.

## Decision

Vendor `shacl12-test-suite/tests` from `w3c/data-shapes` at a pinned commit
with `scripts/sync_suites.py`. Record its URL, commit, commit date and the W3C
Software and Document License in `tests/suite-sources.json`, keep the license
text beside the files and write `tests/w3c12/SHA256SUMS`. Refreshing the suite
is an explicit, reviewed source change. The SHACL 1.0 suite and the 403-case
corrected pySHACL suite are unchanged.

`tests/w3c_grading.py` discovers every manifest entry from the top manifest
and the SPARQL-RL manifests, which the top manifest does not include. Each
entry has a typed `CaseType`; the discovered total of every type is asserted.
Node-expression, inference-rule and SPARQL-RL entries are counted as not-run
with a typed `NotRunReason`, as are Validate cases whose inputs use RDF 1.2
Turtle syntax that RDFLib 7 cannot parse. Discovery reads such files through a
documented lexical projection only to find entries; a projected input is never
executed. Every other Validate case runs through both public `validate`
functions with Graph inputs, graded against the W3C expectation with the SHACL
1.0 report view. A case is pyshacl-parity when both outcomes match, and
beyond-pyshacl when only Turbo passes. Behind-pyshacl and differing failures
are gaps.

`tests/divergences.toml` is the one ledger of differences, loaded into typed
dataclasses and enums by `tests/divergence_ledger.py`. Each entry names its
suite, case ID, kind (intentional or gap), baseline, reason and an existing ADR,
with an optional tracking issue or pull request. The baseline is plain pySHACL
for every suite. The SHACL 1.0 gate additionally lists cases that miss the W3C
expectation; those entries drive its strict `xfail` marks. Reconciliation is
exact in both directions: an unlisted difference fails, and an entry whose case
no longer differs is stale and fails. The SHACL 1.0 and 1.2 suites reconcile in
pytest, the upstream suite in `scripts/check_upstream.py` and the direct
contract in `scripts/compare_contract.py`; pytest also reconciles the committed
upstream and direct-contract records.

Every graded case carries a typed origin. W3C cases are vendored and must be in
the pinned inventory. In the upstream suite, `bad_test_070` is locally corrected
and the two native equivalents are first-party; only vendored cases count as
upstream passes. Direct-contract probes are first-party.

The direct-contract report names the measured pySHACL, facade and provider
versions. A test fails when the reference or provider version differs from the
pins, when the facade version is more than one release behind the project
version, or when its counts drift from its case rows. One release behind is
allowed so the version-only release preparation commit stays green.
`scripts/conformance_report.py` writes `docs/conformance.json` and the README's
per-suite counts from the harness and the ledger; tests fail when either drifts.

## Consequences

Eight of the 31 entries are gaps. Six SHACL 1.2 Validate cases fail
differently: Turbo rejects a list-valued `sh:datatype`, `sh:class`, `sh:nodeKind`,
`sh:equals` or `sh:disjoint` at shape load, where pySHACL loads the shapes and
only misses the W3C expectation. rdflib-turbo 0.2.0a41 (PH-05) ignores unknown
SHACL vocabulary like pySHACL, which removed the 22 entries that its earlier
refusal caused. Grading does not claim SHACL 1.2 conformance: most 1.2 features
are not implemented by either engine.
