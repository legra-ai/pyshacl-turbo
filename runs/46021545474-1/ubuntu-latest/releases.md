# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T15:52:14.978733+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `6bc80f5cba90a7a82f806685609ffcaa4bc4f1ba`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.192 | 9.000–9.301 | 76.59 | equal | 9.71× | — | — |
| pipeline_rdfs | 100 | python-reference | 89.284 | 88.903–93.527 | 55.59 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.220 | 26.553–33.306 | 54.34 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 21.758 | 21.373–22.119 | 77.25 | equal | 9.57× | — | — |
| pipeline_owlrl | 100 | python-reference | 208.244 | 206.488–212.664 | 55.93 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 40.558 | 40.000–44.479 | 54.28 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 270.361 | 264.031–369.538 | 82.28 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 912.765 | 898.448–989.114 | 60.95 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 65.198 | 63.973–67.288 | 80.70 | equal | 14.00× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1437.363 | 1427.860–1549.949 | 62.19 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 137.444 | 136.407–140.498 | 81.21 | equal | 10.46× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 360.901 | 355.799–448.052 | 88.71 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 30.374 | 30.108–31.336 | 52.41 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.258 | 5.159–5.425 | 74.31 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 35.356 | 34.690–35.401 | 86.28 | reference | — | — | — |
| literal-type | 32 | candidate | 5.817 | 5.780–5.923 | 95.78 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 75.933 | 75.505–77.185 | 120.66 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.626 | 8.571–8.655 | 120.66 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.604 | 10.434–10.767 | 229.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 93.840 | 92.814–95.076 | 229.12 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 22.453 | 21.754–22.698 | 340.24 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 253.476 | 250.416–289.500 | 340.24 | reference | — | — | — |
| literal-type | 512 | python-reference | 326.750 | 323.910–363.408 | 656.32 | reference | — | — | — |
| literal-type | 512 | candidate | 30.291 | 29.772–30.682 | 656.32 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 475.248 | 471.623–558.210 | 1064.64 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 40.761 | 39.895–41.241 | 1064.64 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 628.500 | 617.620–636.219 | 1660.12 | reference | — | — | — |
| literal-type | 1000 | candidate | 56.687 | 56.225–57.662 | 1660.12 | different | — | logical_inplace_owlrl_different | — |
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
