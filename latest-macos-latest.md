# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-02T17:29:08.015613+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `1fbe159029984365ffc705388cc1e2b33280c415`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.779 | 10.216–13.721 | 59.53 | equal | 7.83× | — | — |
| pipeline_rdfs | 100 | python-reference | 84.429 | 59.504–125.597 | 60.75 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 23.530 | 18.798–29.145 | 55.55 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.639 | 16.940–20.474 | 60.08 | equal | 8.72× | — | — |
| pipeline_owlrl | 100 | python-reference | 162.605 | 146.264–181.288 | 61.03 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 49.434 | 37.437–97.613 | 57.73 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 317.721 | 244.394–524.483 | 107.16 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 965.225 | 766.370–1323.733 | 66.36 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 89.214 | 72.250–104.835 | 66.22 | equal | 10.82× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1358.459 | 1253.562–1790.629 | 67.33 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 178.840 | 121.601–225.404 | 64.50 | equal | 7.60× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 438.513 | 369.636–509.240 | 118.39 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 27.905 | 24.047–40.716 | 48.95 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 6.332 | 5.271–11.488 | 57.08 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 32.435 | 27.873–41.617 | 49.02 | reference | — | — | — |
| literal-type | 32 | candidate | 5.690 | 5.314–8.276 | 57.17 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 99.517 | 61.571–111.842 | 48.98 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.443 | 7.886–11.026 | 57.42 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 13.214 | 11.396–21.532 | 57.47 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 85.137 | 74.771–94.474 | 48.95 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 25.224 | 22.326–33.813 | 59.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 290.833 | 235.237–322.217 | 50.70 | reference | — | — | — |
| literal-type | 512 | python-reference | 304.401 | 274.299–358.674 | 51.02 | reference | — | — | — |
| literal-type | 512 | candidate | 29.177 | 28.004–41.888 | 60.22 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 415.906 | 343.446–614.146 | 52.69 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 47.395 | 38.821–63.693 | 63.28 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 662.485 | 579.531–801.043 | 53.53 | reference | — | — | — |
| literal-type | 1000 | candidate | 62.419 | 50.517–71.432 | 63.78 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.8.0, rdflib-turbo 0.2.0a30

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
