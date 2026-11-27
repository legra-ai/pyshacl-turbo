# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T23:49:08.279080+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `894649fe91d30496560937ce6899cc355f1541fc`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 13.179 | 7.318–18.825 | 58.09 | equal | 4.74× | — | — |
| pipeline_rdfs | 100 | python-reference | 62.414 | 60.348–76.061 | 59.20 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 28.458 | 19.705–32.846 | 54.75 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.168 | 15.802–18.697 | 58.59 | equal | 10.23× | — | — |
| pipeline_owlrl | 100 | python-reference | 165.462 | 146.838–191.390 | 59.50 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 32.430 | 29.822–35.934 | 56.95 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 202.244 | 188.844–273.051 | 110.88 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 731.691 | 666.278–913.203 | 64.80 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 50.639 | 49.731–55.324 | 63.70 | equal | 14.45× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1053.646 | 1024.745–1232.270 | 65.98 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 95.978 | 93.892–125.650 | 63.16 | equal | 10.98× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 298.377 | 268.406–345.854 | 120.62 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 22.672 | 20.996–28.189 | 47.58 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.414 | 4.256–8.705 | 55.70 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 32.512 | 29.830–38.322 | 47.50 | reference | — | — | — |
| literal-type | 32 | candidate | 4.700 | 4.625–4.993 | 55.86 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 56.803 | 53.858–76.524 | 47.48 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.070 | 6.979–7.665 | 56.11 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.410 | 8.205–14.093 | 56.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 67.072 | 65.876–68.470 | 47.66 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.944 | 16.657–33.192 | 58.78 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 200.383 | 188.632–255.640 | 49.28 | reference | — | — | — |
| literal-type | 512 | python-reference | 258.020 | 237.724–328.868 | 49.44 | reference | — | — | — |
| literal-type | 512 | candidate | 22.435 | 21.698–24.886 | 58.88 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 461.797 | 367.789–641.691 | 51.38 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 33.320 | 31.421–37.791 | 61.98 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 495.036 | 459.410–530.585 | 51.86 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.246 | 40.849–44.488 | 62.69 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.6, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
