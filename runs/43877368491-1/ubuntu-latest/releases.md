# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-16T13:59:57.313225+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `8dbe8d3628800f77a0bee164caaaebff43207eaf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 5.902 | 5.770–5.992 | 76.43 | equal | 8.85× | — | — |
| pipeline_rdfs | 100 | python-reference | 52.212 | 51.570–55.320 | 55.67 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 17.092 | 16.850–20.683 | 54.26 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 14.035 | 13.831–14.256 | 77.21 | equal | 8.70× | — | — |
| pipeline_owlrl | 100 | python-reference | 122.148 | 118.041–123.397 | 55.95 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 24.192 | 23.530–25.839 | 54.37 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 159.245 | 155.052–307.690 | 82.41 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 541.302 | 493.710–615.444 | 61.19 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 42.825 | 40.998–43.781 | 80.58 | equal | 12.64× | — | — |
| pipeline_owlrl | 1000 | python-reference | 887.998 | 814.211–1015.450 | 62.23 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 96.627 | 88.671–99.381 | 81.28 | equal | 9.19× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 220.614 | 204.106–327.571 | 89.00 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 17.100 | 17.061–17.284 | 51.94 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.604 | 3.552–3.662 | 74.18 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 19.895 | 19.771–20.044 | 85.69 | reference | — | — | — |
| literal-type | 32 | candidate | 3.647 | 3.596–3.801 | 95.32 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 44.820 | 44.301–45.323 | 119.94 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.086 | 6.041–6.125 | 119.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 6.991 | 6.795–7.029 | 228.22 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 55.611 | 54.493–55.889 | 228.22 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 14.815 | 14.701–14.961 | 339.44 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 143.932 | 141.484–179.982 | 339.44 | reference | — | — | — |
| literal-type | 512 | python-reference | 184.462 | 183.002–227.570 | 655.85 | reference | — | — | — |
| literal-type | 512 | candidate | 20.349 | 20.155–21.546 | 655.85 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 268.266 | 267.018–354.848 | 1064.17 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 26.453 | 26.105–26.680 | 1064.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 348.032 | 345.481–377.216 | 1659.14 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.019 | 37.010–38.906 | 1659.14 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.2, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
