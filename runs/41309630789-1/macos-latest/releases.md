# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-01T15:18:23.848806+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `9d5910e6b6b2e011859a8b3b8a5b7251cb5d4d5b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.824 | 8.365–11.807 | 59.33 | equal | 5.57× | — | — |
| pipeline_rdfs | 100 | python-reference | 54.757 | 53.117–64.387 | 60.78 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 19.272 | 19.012–22.972 | 55.97 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.842 | 17.445–20.869 | 59.80 | equal | 8.18× | — | — |
| pipeline_owlrl | 100 | python-reference | 154.169 | 141.165–160.585 | 61.08 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 35.299 | 33.368–36.600 | 58.28 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 231.355 | 184.633–321.376 | 111.42 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 752.666 | 674.419–979.706 | 66.25 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 85.053 | 74.231–91.865 | 66.28 | equal | 8.85× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1125.812 | 1070.254–1200.802 | 67.33 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 106.723 | 97.127–112.543 | 64.25 | equal | 10.55× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 329.075 | 276.132–472.348 | 121.84 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 22.123 | 22.002–26.415 | 49.22 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.025 | 4.557–5.298 | 57.03 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 26.614 | 24.590–31.939 | 49.11 | reference | — | — | — |
| literal-type | 32 | candidate | 7.962 | 5.164–8.904 | 56.97 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 55.828 | 51.879–64.136 | 49.16 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.957 | 7.769–9.160 | 57.11 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.625 | 9.590–10.028 | 57.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 68.589 | 64.210–92.613 | 48.98 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 25.683 | 22.525–28.850 | 59.78 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 240.907 | 178.860–277.145 | 50.73 | reference | — | — | — |
| literal-type | 512 | python-reference | 237.746 | 226.871–367.979 | 50.92 | reference | — | — | — |
| literal-type | 512 | candidate | 24.594 | 23.637–34.828 | 60.20 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 436.695 | 363.803–604.584 | 52.98 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 33.672 | 31.901–35.026 | 63.02 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 478.453 | 453.694–591.761 | 53.45 | reference | — | — | — |
| literal-type | 1000 | candidate | 45.835 | 44.210–48.398 | 63.61 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.5, rdflib-turbo 0.2.0a27

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
