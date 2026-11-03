# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-03T17:00:39.378139+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `8f03cd4296b36764950306219408eefd65624b28`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.841 | 10.082–15.571 | 66.35 | equal | 10.72× | — | — |
| pipeline_rdfs | 100 | python-reference | 116.179 | 114.661–117.287 | 47.33 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 32.113 | 31.644–38.265 | 44.18 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 29.037 | 26.652–33.168 | 66.84 | equal | 9.61× | — | — |
| pipeline_owlrl | 100 | python-reference | 279.081 | 275.396–284.201 | 47.67 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 48.442 | 47.111–53.148 | 45.39 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 322.898 | 319.779–443.903 | 73.86 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1168.807 | 1144.333–1239.428 | 52.85 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 75.620 | 73.716–81.383 | 71.08 | equal | 15.46× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1931.052 | 1925.033–2058.882 | 53.89 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 199.751 | 169.190–325.103 | 71.70 | equal | 9.67× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 433.504 | 429.135–552.701 | 80.35 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 41.316 | 41.006–42.945 | 42.76 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.988 | 5.810–7.496 | 64.88 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 49.011 | 48.334–50.018 | 76.51 | reference | — | — | — |
| literal-type | 32 | candidate | 6.621 | 6.496–7.477 | 86.01 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 100.642 | 99.680–102.266 | 110.76 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.908 | 9.516–10.659 | 110.76 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 12.682 | 12.177–14.725 | 218.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 127.109 | 125.173–128.567 | 218.97 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 27.955 | 25.466–30.412 | 330.29 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 340.952 | 336.760–394.490 | 330.29 | reference | — | — | — |
| literal-type | 512 | python-reference | 445.025 | 439.900–495.658 | 646.89 | reference | — | — | — |
| literal-type | 512 | candidate | 38.010 | 35.057–39.602 | 646.89 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 642.583 | 636.434–755.025 | 1055.20 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 48.572 | 48.118–50.415 | 1055.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 843.376 | 837.741–854.230 | 1650.31 | reference | — | — | — |
| literal-type | 1000 | candidate | 69.619 | 67.888–73.058 | 1650.31 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.9.1, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
