# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-06T14:07:31.944177+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `bc9ec2d32b8345fcaf7a4f0aaac62f273cce658e`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.483 | 7.280–10.901 | 59.48 | equal | 7.93× | — | — |
| pipeline_rdfs | 100 | python-reference | 67.308 | 64.651–93.630 | 60.92 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 28.965 | 25.632–41.939 | 55.95 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 19.105 | 18.368–25.435 | 60.08 | equal | 10.89× | — | — |
| pipeline_owlrl | 100 | python-reference | 208.049 | 182.094–252.981 | 61.17 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 51.371 | 37.312–66.423 | 58.12 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 245.736 | 199.074–326.568 | 111.41 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1058.416 | 727.710–1260.053 | 66.39 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 80.557 | 72.259–100.606 | 65.36 | equal | 13.14× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1453.303 | 1310.331–1551.075 | 67.56 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 134.725 | 115.598–149.001 | 64.56 | equal | 10.79× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 423.595 | 327.344–522.950 | 120.27 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3756.036 | 3074.915–4823.607 | 682.94 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 23765.477 | 20968.811–29558.103 | 142.09 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 569.139 | 486.267–767.086 | 130.23 | equal | 41.76× | — | — |
| pipeline_owlrl | 10000 | python-reference | 12566.227 | 11046.213–16090.400 | 151.20 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1191.375 | 1094.623–1608.552 | 122.70 | equal | 10.55× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5048.739 | 4552.761–5275.941 | 787.52 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 25.269 | 23.758–29.117 | 49.06 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.781 | 5.162–12.777 | 57.02 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 5.114 | 4.966–5.446 | 57.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 28.716 | 27.643–31.701 | 49.06 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.352 | 8.124–10.157 | 57.41 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 56.932 | 55.403–58.758 | 49.19 | reference | — | — | — |
| literal-type | 128 | python-reference | 84.597 | 73.737–88.990 | 49.03 | reference | — | — | — |
| literal-type | 128 | candidate | 10.657 | 9.712–11.326 | 57.50 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 208.958 | 185.238–241.148 | 50.67 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 23.363 | 22.368–24.352 | 60.05 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 245.852 | 235.210–279.270 | 51.00 | reference | — | — | — |
| literal-type | 512 | candidate | 25.545 | 24.631–27.704 | 60.34 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 34.506 | 31.835–41.426 | 63.42 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 440.473 | 349.038–477.353 | 52.97 | reference | — | — | — |
| literal-type | 1000 | candidate | 48.136 | 45.888–53.000 | 63.91 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 483.042 | 434.288–555.174 | 53.45 | reference | — | — | — |
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
