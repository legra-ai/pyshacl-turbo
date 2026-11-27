# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T10:11:24.527878+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `e44f35858166d02881cd2725dcf9db2d6863d6e4`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 5.874 | 5.719–6.096 | 76.59 | equal | 8.57× | — | — |
| pipeline_rdfs | 100 | python-reference | 50.327 | 49.858–54.134 | 55.69 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 15.910 | 15.448–18.917 | 55.28 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.055 | 14.578–15.511 | 77.25 | equal | 7.67× | — | — |
| pipeline_owlrl | 100 | python-reference | 115.535 | 115.194–119.072 | 55.89 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 23.840 | 23.114–26.707 | 55.27 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 158.687 | 152.217–253.980 | 83.55 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 505.817 | 499.907–599.116 | 61.16 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 41.631 | 40.878–42.803 | 80.62 | equal | 12.15× | — | — |
| pipeline_owlrl | 1000 | python-reference | 840.066 | 808.314–975.024 | 62.22 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 91.526 | 90.188–96.695 | 81.45 | equal | 9.18× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 230.506 | 213.003–315.604 | 89.93 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 18.191 | 17.897–18.354 | 52.28 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.471 | 3.404–3.550 | 74.41 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 20.923 | 20.750–21.068 | 86.28 | reference | — | — | — |
| literal-type | 32 | candidate | 3.858 | 3.838–4.092 | 95.78 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 43.566 | 43.225–44.688 | 120.66 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.016 | 5.899–6.134 | 120.66 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.488 | 7.374–7.606 | 228.98 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 53.995 | 52.724–55.309 | 228.98 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 15.864 | 15.699–16.045 | 340.30 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 149.366 | 146.622–229.178 | 340.30 | reference | — | — | — |
| literal-type | 512 | python-reference | 196.135 | 188.728–263.927 | 656.45 | reference | — | — | — |
| literal-type | 512 | candidate | 22.280 | 21.200–23.841 | 656.45 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 285.714 | 282.399–397.233 | 1064.77 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 27.643 | 27.072–27.964 | 1064.77 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 374.163 | 371.071–395.791 | 1660.19 | reference | — | — | — |
| literal-type | 1000 | candidate | 40.564 | 39.111–42.642 | 1660.19 | different | — | logical_inplace_owlrl_different | — |
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
