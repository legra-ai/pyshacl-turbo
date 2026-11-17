# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-17T13:51:03.373544+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `e1fb11c010847556649f363b914b1421b7cb59ae`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.285 | 7.169–11.356 | 76.47 | equal | 9.46× | — | — |
| pipeline_rdfs | 100 | python-reference | 68.882 | 67.762–73.161 | 55.63 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.432 | 21.183–26.665 | 54.05 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.405 | 16.016–16.561 | 76.88 | equal | 9.87× | — | — |
| pipeline_owlrl | 100 | python-reference | 161.941 | 161.020–165.393 | 55.94 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.471 | 33.350–38.163 | 54.11 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 225.016 | 207.584–340.386 | 82.39 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 734.065 | 715.681–806.272 | 61.14 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 54.013 | 53.012–55.176 | 80.50 | equal | 13.59× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1135.664 | 1120.795–1261.563 | 62.21 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 102.077 | 100.805–106.904 | 81.01 | equal | 11.13× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 306.455 | 296.742–394.099 | 88.92 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3587.475 | 3357.649–3718.361 | 400.62 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 19615.692 | 19406.769–20084.590 | 126.60 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 662.927 | 631.575–709.675 | 123.74 | equal | 29.59× | — | — |
| pipeline_owlrl | 10000 | python-reference | 11478.395 | 11403.410–11732.343 | 135.12 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1257.449 | 1231.781–1754.108 | 124.49 | equal | 9.13× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 4978.986 | 4864.018–5066.719 | 459.37 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.230 | 23.644–24.663 | 173.77 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.042 | 3.923–4.075 | 173.77 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.474 | 4.405–4.587 | 206.56 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 28.025 | 27.562–28.620 | 206.56 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.693 | 6.555–6.779 | 245.20 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 60.382 | 60.196–61.969 | 245.20 | reference | — | — | — |
| literal-type | 128 | python-reference | 75.247 | 74.273–76.059 | 333.85 | reference | — | — | — |
| literal-type | 128 | candidate | 8.247 | 8.201–8.342 | 333.85 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 199.744 | 198.607–237.181 | 444.59 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.517 | 17.215–18.350 | 444.59 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 257.179 | 254.766–296.594 | 757.66 | reference | — | — | — |
| literal-type | 512 | candidate | 23.597 | 23.209–23.718 | 757.66 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 32.016 | 31.300–44.101 | 1158.95 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 384.867 | 378.806–468.756 | 1158.95 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.246 | 42.992–43.800 | 1757.86 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 495.856 | 487.763–511.810 | 1757.86 | reference | — | — | — |
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
