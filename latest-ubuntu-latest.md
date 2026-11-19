# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-19T14:09:44.012563+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.558 | 7.225–11.709 | 76.60 | equal | 9.12× | — | — |
| pipeline_rdfs | 100 | python-reference | 68.942 | 67.901–72.072 | 55.71 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 22.002 | 21.435–28.100 | 54.21 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.497 | 16.220–16.629 | 77.35 | equal | 9.90× | — | — |
| pipeline_owlrl | 100 | python-reference | 163.383 | 161.981–178.970 | 56.00 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.662 | 33.089–37.797 | 54.24 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 228.504 | 215.696–325.070 | 82.45 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 719.432 | 709.986–803.757 | 61.14 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 54.791 | 53.674–57.094 | 80.67 | equal | 13.13× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1147.387 | 1129.527–1262.007 | 62.16 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 105.973 | 102.938–118.023 | 81.35 | equal | 10.83× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 303.366 | 287.672–381.272 | 88.83 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3536.804 | 3482.900–3704.318 | 400.84 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 19488.977 | 19363.019–19696.482 | 126.51 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 690.524 | 666.536–1130.555 | 123.90 | equal | 28.22× | — | — |
| pipeline_owlrl | 10000 | python-reference | 11492.406 | 11353.426–11659.526 | 135.11 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1302.058 | 1251.675–1761.390 | 124.96 | equal | 8.83× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5280.139 | 5197.780–5425.940 | 458.32 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.498 | 24.245–24.908 | 162.46 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.021 | 3.919–4.185 | 162.46 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.495 | 4.406–4.573 | 195.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 28.055 | 27.786–28.313 | 195.20 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.738 | 6.467–6.848 | 233.98 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 60.530 | 59.205–62.297 | 233.98 | reference | — | — | — |
| literal-type | 128 | python-reference | 74.670 | 73.751–75.910 | 322.52 | reference | — | — | — |
| literal-type | 128 | candidate | 8.325 | 8.200–8.596 | 322.52 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 201.576 | 200.510–247.363 | 433.26 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.466 | 17.275–17.582 | 433.26 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 259.279 | 257.356–297.611 | 751.09 | reference | — | — | — |
| literal-type | 512 | candidate | 23.498 | 23.292–24.972 | 751.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 31.641 | 31.081–32.070 | 1159.34 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 384.357 | 377.451–491.316 | 1159.34 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.325 | 43.147–44.186 | 1758.29 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 497.802 | 492.772–504.144 | 1758.29 | reference | — | — | — |
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
