# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-18T14:47:37.976915+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `e05b5b7519ce737be6d4cd51458cb0c71e59bcc2`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.313 | 6.904–12.057 | 58.03 | equal | 6.59× | — | — |
| pipeline_rdfs | 100 | python-reference | 67.941 | 61.617–80.221 | 59.31 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 23.817 | 22.213–31.135 | 54.58 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.434 | 15.527–25.799 | 58.59 | equal | 9.09× | — | — |
| pipeline_owlrl | 100 | python-reference | 167.470 | 150.089–181.551 | 59.64 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 35.076 | 34.264–40.581 | 56.83 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 260.417 | 217.240–310.286 | 109.47 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 757.419 | 690.361–899.242 | 64.83 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 53.851 | 48.551–56.911 | 63.52 | equal | 14.07× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1230.070 | 1093.336–1489.433 | 65.91 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 110.497 | 91.619–145.208 | 63.06 | equal | 11.13× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 312.554 | 261.567–391.041 | 118.89 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 23.211 | 21.292–32.701 | 47.66 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 7.528 | 5.121–9.885 | 55.86 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 25.548 | 24.903–29.612 | 47.64 | reference | — | — | — |
| literal-type | 32 | candidate | 5.456 | 5.167–7.051 | 55.89 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 59.391 | 57.554–70.640 | 47.67 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.708 | 6.599–6.803 | 56.16 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.823 | 8.518–13.930 | 56.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 68.409 | 64.959–82.304 | 47.69 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.431 | 16.109–19.239 | 58.73 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 201.268 | 183.995–232.759 | 49.25 | reference | — | — | — |
| literal-type | 512 | python-reference | 271.129 | 259.210–345.429 | 49.56 | reference | — | — | — |
| literal-type | 512 | candidate | 27.291 | 23.321–29.091 | 59.05 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 404.844 | 342.754–466.113 | 51.55 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 34.482 | 29.195–37.961 | 62.05 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 535.557 | 499.456–757.650 | 52.05 | reference | — | — | — |
| literal-type | 1000 | candidate | 39.592 | 38.217–58.645 | 62.47 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 32 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-type | 32 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-reflexivity | 128 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-type | 128 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-reflexivity | 512 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-type | 512 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-reflexivity | 1000 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-type | 1000 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
