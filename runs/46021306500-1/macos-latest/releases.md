# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T15:26:01.391478+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `6bc80f5cba90a7a82f806685609ffcaa4bc4f1ba`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 6.685 | 6.295–9.296 | 57.95 | equal | 16.94× | — | — |
| pipeline_rdfs | 100 | python-reference | 113.263 | 76.723–129.883 | 59.23 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.371 | 18.876–22.553 | 54.73 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.501 | 15.390–16.176 | 58.61 | equal | 8.40× | — | — |
| pipeline_owlrl | 100 | python-reference | 130.263 | 128.688–138.643 | 59.56 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 29.810 | 29.004–31.290 | 56.95 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 198.498 | 174.873–243.910 | 109.98 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 736.299 | 679.686–842.297 | 64.80 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 55.863 | 53.358–62.963 | 63.94 | equal | 13.18× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1559.875 | 1410.917–2173.110 | 65.92 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 101.967 | 94.081–143.894 | 63.09 | equal | 15.30× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 303.839 | 281.491–383.201 | 119.30 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 21.792 | 20.432–24.508 | 47.56 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.664 | 4.271–6.433 | 55.89 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 24.099 | 23.075–26.913 | 47.58 | reference | — | — | — |
| literal-type | 32 | candidate | 4.765 | 4.324–5.734 | 55.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 71.417 | 64.071–107.702 | 47.59 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.793 | 6.484–7.903 | 56.16 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.684 | 7.736–10.740 | 56.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 63.571 | 62.951–67.088 | 47.52 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 15.562 | 14.859–17.422 | 58.83 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 210.726 | 180.393–274.869 | 49.28 | reference | — | — | — |
| literal-type | 512 | python-reference | 235.000 | 231.055–275.661 | 49.47 | reference | — | — | — |
| literal-type | 512 | candidate | 22.229 | 21.358–24.174 | 59.03 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 335.364 | 329.706–410.786 | 51.41 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 28.763 | 27.446–40.134 | 62.06 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 441.233 | 423.497–470.571 | 51.97 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.753 | 37.834–45.249 | 62.52 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.6, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
