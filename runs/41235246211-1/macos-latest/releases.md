# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T19:59:04.863274+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `d8a3c162ae4518949f8e3fdb6ae515a515722696`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.421 | 8.175–10.707 | 59.23 | equal | 7.07× | — | — |
| pipeline_rdfs | 100 | python-reference | 59.541 | 58.138–62.558 | 60.88 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 16.950 | 16.738–20.219 | 55.97 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.165 | 14.986–15.392 | 59.80 | equal | 8.41× | — | — |
| pipeline_owlrl | 100 | python-reference | 127.475 | 126.257–133.452 | 61.14 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 27.517 | 26.262–28.967 | 58.17 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 180.962 | 160.323–211.914 | 111.53 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 566.298 | 554.439–721.420 | 66.33 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 64.225 | 63.216–64.593 | 65.97 | equal | 8.82× | — | — |
| pipeline_owlrl | 1000 | python-reference | 902.878 | 874.197–953.760 | 67.44 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 89.350 | 88.527–92.038 | 64.20 | equal | 10.10× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 251.395 | 215.722–294.717 | 121.27 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 19.046 | 18.756–19.852 | 49.17 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.758 | 3.743–3.834 | 57.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.199 | 21.812–24.756 | 49.16 | reference | — | — | — |
| literal-type | 32 | candidate | 4.877 | 4.732–6.481 | 57.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 53.569 | 51.094–57.485 | 49.23 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.848 | 7.451–9.289 | 57.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.881 | 7.771–7.908 | 57.38 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 60.054 | 58.039–62.036 | 49.17 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.035 | 18.335–21.082 | 59.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 154.811 | 153.224–175.932 | 50.83 | reference | — | — | — |
| literal-type | 512 | python-reference | 203.111 | 201.859–224.495 | 51.11 | reference | — | — | — |
| literal-type | 512 | candidate | 25.859 | 22.193–27.169 | 60.20 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 302.106 | 292.742–669.195 | 52.95 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 31.814 | 28.595–33.111 | 63.27 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 390.058 | 388.326–393.000 | 53.56 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.880 | 38.651–42.594 | 63.75 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.1, rdflib-turbo 0.2.0a23

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
