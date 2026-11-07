# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-07T11:30:12.301481+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `bc9ec2d32b8345fcaf7a4f0aaac62f273cce658e`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 6.312 | 5.934–8.493 | 59.39 | equal | 9.52× | — | — |
| pipeline_rdfs | 100 | python-reference | 60.070 | 57.441–62.646 | 60.78 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 22.005 | 19.929–24.673 | 55.89 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.514 | 17.390–19.079 | 59.97 | equal | 8.41× | — | — |
| pipeline_owlrl | 100 | python-reference | 147.276 | 144.813–170.308 | 61.11 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 30.379 | 27.792–33.781 | 58.17 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 202.907 | 170.692–281.641 | 110.80 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 635.745 | 606.376–724.041 | 66.30 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 55.594 | 43.705–59.700 | 64.92 | equal | 11.44× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1048.108 | 978.142–1327.505 | 67.41 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 101.504 | 92.908–105.445 | 64.45 | equal | 10.33× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 290.821 | 255.080–304.031 | 121.00 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3242.433 | 2809.070–3409.564 | 684.03 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 17008.567 | 16869.418–17299.755 | 141.95 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 549.509 | 524.734–775.358 | 129.64 | equal | 30.95× | — | — |
| pipeline_owlrl | 10000 | python-reference | 10514.745 | 10230.415–10760.300 | 150.95 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1038.222 | 1021.517–1303.864 | 122.47 | equal | 10.13× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 4116.070 | 3616.989–4446.398 | 789.23 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.839 | 20.970–29.285 | 49.11 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.499 | 4.289–5.695 | 57.14 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.813 | 4.721–5.027 | 57.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 23.808 | 22.970–27.088 | 49.12 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.432 | 6.944–8.859 | 57.39 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 47.636 | 45.803–54.514 | 49.12 | reference | — | — | — |
| literal-type | 128 | python-reference | 86.168 | 76.557–96.151 | 49.17 | reference | — | — | — |
| literal-type | 128 | candidate | 9.352 | 8.754–10.417 | 57.52 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 177.895 | 167.784–208.569 | 50.70 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 23.048 | 22.238–26.303 | 60.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 275.686 | 257.237–310.807 | 51.02 | reference | — | — | — |
| literal-type | 512 | candidate | 30.291 | 28.285–31.606 | 60.33 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 40.001 | 34.275–44.517 | 63.30 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 395.717 | 360.662–429.839 | 52.95 | reference | — | — | — |
| literal-type | 1000 | candidate | 48.244 | 44.914–57.165 | 63.88 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 525.790 | 505.620–558.828 | 53.50 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.10.0, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
