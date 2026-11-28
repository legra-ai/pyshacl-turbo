# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T09:46:35.028497+00:00; platform: Linux-7.0.0-1018-aws-x86_64-with-glibc2.43.
Harness revision: `985a797fe6b5b0372f267476bfbaf0ff367df8d6`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.711 | 7.396–7.847 | 77.42 | equal | 9.27× | — | — |
| pipeline_rdfs | 100 | python-reference | 71.463 | 69.825–74.269 | 55.89 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.899 | 20.613–25.218 | 54.41 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.936 | 16.684–17.348 | 78.57 | equal | 9.82× | — | — |
| pipeline_owlrl | 100 | python-reference | 166.351 | 163.614–170.505 | 56.12 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 31.994 | 31.729–34.953 | 54.43 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 219.170 | 214.542–303.984 | 82.63 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 747.236 | 734.459–815.074 | 61.28 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 52.357 | 51.925–53.651 | 81.54 | equal | 14.27× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1167.312 | 1149.242–1245.267 | 62.29 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 108.620 | 107.762–110.629 | 82.55 | equal | 10.75× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 291.105 | 285.589–357.260 | 88.97 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.864 | 24.171–25.181 | 52.31 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.110 | 3.985–4.327 | 74.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 28.204 | 28.045–28.611 | 86.19 | reference | — | — | — |
| literal-type | 32 | candidate | 4.555 | 4.435–4.668 | 95.69 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 60.085 | 59.452–61.532 | 120.56 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.972 | 6.850–7.178 | 120.56 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.530 | 8.275–9.064 | 228.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 75.338 | 74.149–76.126 | 228.97 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.295 | 17.182–17.966 | 340.52 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 201.455 | 201.190–237.503 | 340.52 | reference | — | — | — |
| literal-type | 512 | python-reference | 265.880 | 254.878–291.851 | 656.62 | reference | — | — | — |
| literal-type | 512 | candidate | 23.434 | 23.135–23.696 | 656.62 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 389.033 | 377.271–453.018 | 1064.89 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 32.099 | 31.916–32.879 | 1064.89 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 496.150 | 491.727–505.798 | 1660.43 | reference | — | — | — |
| literal-type | 1000 | candidate | 44.966 | 44.223–45.192 | 1660.43 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.9, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
