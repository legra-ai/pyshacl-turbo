# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-02T16:15:18.170043+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `9d5910e6b6b2e011859a8b3b8a5b7251cb5d4d5b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 12.833 | 11.752–18.153 | 59.45 | equal | 5.67× | — | — |
| pipeline_rdfs | 100 | python-reference | 72.796 | 69.947–75.762 | 60.75 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 24.529 | 22.828–50.727 | 55.73 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 24.770 | 24.153–25.348 | 59.78 | equal | 7.30× | — | — |
| pipeline_owlrl | 100 | python-reference | 180.716 | 160.990–235.634 | 61.06 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 33.350 | 30.192–37.032 | 58.25 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 231.579 | 205.446–311.363 | 111.44 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 793.347 | 752.331–963.757 | 66.22 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 90.160 | 76.229–143.405 | 66.06 | equal | 8.80× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1191.399 | 1092.362–1570.706 | 67.36 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 106.671 | 104.419–125.190 | 64.20 | equal | 11.17× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 317.977 | 283.547–420.052 | 120.25 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3797.990 | 3682.961–4048.887 | 689.88 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 33086.797 | 22134.525–35788.460 | 141.89 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 970.414 | 815.829–1291.731 | 142.12 | equal | 34.10× | — | — |
| pipeline_owlrl | 10000 | python-reference | 12606.374 | 11475.875–15462.434 | 150.92 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1448.237 | 1201.402–1617.748 | 122.56 | equal | 8.70× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 4830.907 | 4265.117–6034.469 | 766.52 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 23.574 | 21.209–38.073 | 49.12 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.180 | 5.107–8.464 | 56.88 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 5.045 | 4.958–5.905 | 56.92 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 24.321 | 23.857–26.757 | 49.17 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.211 | 8.209–11.323 | 57.23 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 56.206 | 54.972–59.518 | 49.09 | reference | — | — | — |
| literal-type | 128 | python-reference | 85.244 | 71.483–112.501 | 49.12 | reference | — | — | — |
| literal-type | 128 | candidate | 9.472 | 8.688–11.489 | 57.34 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 184.485 | 176.695–302.082 | 50.69 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 20.708 | 19.943–27.246 | 59.78 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 262.436 | 240.623–304.391 | 51.09 | reference | — | — | — |
| literal-type | 512 | candidate | 24.506 | 24.013–27.794 | 60.19 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 35.331 | 32.310–45.293 | 63.00 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 372.040 | 328.106–442.343 | 52.95 | reference | — | — | — |
| literal-type | 1000 | candidate | 63.204 | 55.699–70.276 | 63.64 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 529.590 | 452.649–598.415 | 53.52 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.5, rdflib-turbo 0.2.0a27

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
