# Inference memory: journaled additions and distinct new results

The [runtime change](https://github.com/legra-ai/rdflib-turbo/pull/12) removes the
full-dataset inference snapshot and duplicate/already-known round buffers.
Default-graph inference retains one dataset and a compact insertion journal.
Errors and unwinding roll back new quads and interned terms; named graphs retain
one required union view. See runtime ADR 0005 and its allocation-budget tests.

## Installed-wheel pipeline results

Both runs used the same harness revision `8c43b9487a0f19db9d42d2af9aa111133efe69d5`
on macOS arm64 with CPython 3.13.0. The complete operation is parse → in-place
inference → SHACL compilation/validation → public report output. Shape-document
parsing is setup. Each harness run finishes its builds and integration tests before timings. Seven retained timing
samples follow one warmup; three independent cold workers measure process peak
RSS before full observation encoding. Every sample is retained.

| Inference | Records | Before MiB | After MiB | Python MiB | Before median ms | After median ms |
|---|---:|---:|---:|---:|---:|---:|
| rdfs | 1,000 | 64.48 | 57.05 | 54.41 | 49.54 | 40.04 |
| owlrl | 1,000 | 77.86 | 59.22 | 56.08 | 84.34 | 59.37 |
| rdfs | 10,000 | 254.50 | 170.19 | 135.69 | 653.97 | 462.43 |
| owlrl | 10,000 | 324.73 | 197.83 | 142.98 | 951.53 | 774.91 |

The Python column is the after-run reference; both reference measurements are
retained in the raw reports. All four candidate cases produced identical,
stable complete observations before/after, including inferred RDF, complete
report graphs and report text. Known generalized-RDF/text differences from the
original Python trio remain visible and withhold full-output ratios versus
Python. These synthetic results are descriptive measurements on one host.

Memory is substantially lower and still exceeds Python: at 10,000 records the
OWL-RL pipeline uses about 198 MiB versus Python's 143 MiB. The runtime retains
six ordered quad indexes, query intermediates and reporting allocations.

## Requested native Rust heap

A separate opt-in release test binary counts requested Rust allocations by phase.
It excludes Python allocations, allocator arena/relocation overhead and facade
RDFLib report decoding; these numbers are not process RSS. Source revisions and
fixture hashes are in the four native JSON files below. Both inputs, inferred
quad counts and clean-source checks agree between each before/after pair.

| Records | Inference peak before MiB | After MiB | Reduction |
|---|---:|---:|---:|
| 1,000 | 20.81 | 9.62 | 53.8% |
| 10,000 | 199.70 | 103.36 | 48.2% |

At 10,000 records retained native heap after inference is still about 69 MiB;
the main reduction is transient duplication. The CI allocation-budget test fails
on the original implementation and passes on the journaled implementation.

## Source and artifact provenance

The native runtime changes from `33fd54243a56535c40cd3aa5266ba09538c57084`
to `107a382acb42282069f5be3a58a51f687ef3e14e`. Both preview wheels have version
0.2.0a1 and are distinguished by their source/wheel/native identities. The final
coordinated runtime pin adds CI/portable-test changes to the same production
implementation. The OWL-RL wheel is byte-identical across the two sets.

The pySHACL Python payload and native extension are byte-identical across sets;
only SBOM metadata and its RECORD entry differ. Its recorded checkout HEAD is
`6d70c357ac40829c5a14bb6c8f68a91c52d68ac8`. The after archive was built with a
benchmark source-pin manifest edit matching committed tree `6190cd0`; that edit
does not enter the installed runtime payload. All exact wheel/native hashes are
retained. The builder now rejects dirty inputs and builds every archive from an
isolated committed Git checkout, so future source identity is unambiguous.

The measured harness used the `unique-anchors-v1` complete-graph encoder, with
RDFLib canonicalization for ambiguous graphs. Its method is recorded in each
digest. Legacy catalogue checks retain their original `rdflib-v1` wire format
and immutable baseline. No sample's output check is omitted.

## Evidence and reproduction

- [Before report](memory-evidence/pipeline-before.md) and [raw JSON.gz](memory-evidence/pipeline-before.json.gz).
- [After report](memory-evidence/pipeline-after.md) and [raw JSON.gz](memory-evidence/pipeline-after.json.gz).
- [Before locks](memory-evidence/locks/before) and [after locks](memory-evidence/locks/after).
- Native heap: [before 1,000](memory-evidence/native-before-1000.json), [after 1,000](memory-evidence/native-after-1000.json), [before 10,000](memory-evidence/native-before-10000.json), [after 10,000](memory-evidence/native-after-10000.json).

Use the coordinated wheel builder with the recorded source pins, then run
`benchmarks/releases.py --candidate-wheels WHEELS --integration-tests integration
--nodes 1000 10000 --repeats 7 --memory-repeats 3 --timeout 900 --output REPORT`.
The [benchmark guide](releases.md) describes the uv commands. Native phase
profiles use rdflib-turbo's `scripts/profile_memory.py` with the canonical
`companions.py` fixture and SHAPES document; their hashes identify those inputs.
