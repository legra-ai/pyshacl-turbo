# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T15:15:49.343141+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `6bc80f5cba90a7a82f806685609ffcaa4bc4f1ba`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.907 | 6.556–15.018 | 76.60 | equal | 4.68× | — | — |
| pipeline_rdfs | 100 | python-reference | 51.044 | 49.883–52.103 | 55.64 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 15.757 | 15.194–19.498 | 54.19 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.222 | 15.767–27.437 | 77.27 | equal | 5.96× | — | — |
| pipeline_owlrl | 100 | python-reference | 120.445 | 118.229–123.298 | 55.89 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 24.668 | 22.829–36.000 | 54.24 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 156.141 | 149.804–237.392 | 82.39 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 511.492 | 495.170–649.248 | 61.05 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 58.328 | 52.695–69.352 | 80.61 | equal | 8.77× | — | — |
| pipeline_owlrl | 1000 | python-reference | 811.374 | 793.008–923.056 | 62.13 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 115.068 | 105.359–137.939 | 81.10 | equal | 7.05× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 219.179 | 207.271–298.322 | 89.05 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 17.118 | 16.974–17.237 | 52.68 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.862 | 3.951–8.798 | 74.42 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 20.990 | 20.692–21.326 | 86.43 | reference | — | — | — |
| literal-type | 32 | candidate | 8.230 | 5.396–10.255 | 95.80 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 43.777 | 41.660–44.761 | 120.68 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.851 | 6.473–11.465 | 120.68 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.619 | 7.769–21.655 | 229.35 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 52.660 | 51.876–54.408 | 229.35 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 25.063 | 16.496–30.745 | 340.48 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 144.360 | 140.649–188.229 | 340.48 | reference | — | — | — |
| literal-type | 512 | python-reference | 195.124 | 180.674–235.109 | 656.59 | reference | — | — | — |
| literal-type | 512 | candidate | 30.039 | 22.520–39.313 | 656.59 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 280.732 | 271.234–384.168 | 1064.89 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 41.989 | 34.763–48.910 | 1064.89 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 355.616 | 343.230–367.563 | 1660.50 | reference | — | — | — |
| literal-type | 1000 | candidate | 51.530 | 42.595–61.909 | 1660.50 | different | — | logical_inplace_owlrl_different | — |
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
