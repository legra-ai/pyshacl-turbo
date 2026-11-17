# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-17T13:06:07.166919+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `e1fb11c010847556649f363b914b1421b7cb59ae`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.220 | 8.991–9.696 | 76.48 | equal | 10.44× | — | — |
| pipeline_rdfs | 100 | python-reference | 96.215 | 94.334–98.809 | 55.68 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.772 | 26.982–32.349 | 54.15 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.191 | 19.873–21.514 | 77.17 | equal | 10.88× | — | — |
| pipeline_owlrl | 100 | python-reference | 219.678 | 218.017–221.721 | 55.93 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 42.206 | 41.477–45.564 | 54.18 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 270.972 | 263.145–351.377 | 82.59 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 999.384 | 991.429–1086.014 | 61.09 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 65.154 | 65.012–67.629 | 80.58 | equal | 15.34× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1524.073 | 1520.132–1628.359 | 62.18 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 125.108 | 123.780–126.373 | 81.05 | equal | 12.18× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 361.097 | 355.107–433.557 | 88.94 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 33.282 | 33.057–33.626 | 52.21 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.848 | 4.759–4.889 | 74.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 37.731 | 37.387–39.535 | 85.96 | reference | — | — | — |
| literal-type | 32 | candidate | 5.476 | 5.401–5.595 | 95.46 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 79.607 | 79.081–81.662 | 120.21 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.168 | 8.077–8.334 | 120.21 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.243 | 9.987–13.805 | 228.31 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 100.492 | 99.858–101.271 | 228.31 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.225 | 20.968–21.424 | 339.59 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 265.172 | 264.986–291.705 | 339.59 | reference | — | — | — |
| literal-type | 512 | python-reference | 351.324 | 348.887–380.742 | 656.05 | reference | — | — | — |
| literal-type | 512 | candidate | 29.069 | 28.632–29.509 | 656.05 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 512.245 | 503.298–575.818 | 1064.39 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 38.357 | 37.920–38.690 | 1064.39 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 659.311 | 652.132–663.396 | 1659.41 | reference | — | — | — |
| literal-type | 1000 | candidate | 53.352 | 52.752–55.029 | 1659.41 | different | — | logical_inplace_owlrl_different | — |
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
