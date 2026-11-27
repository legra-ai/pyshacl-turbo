# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T12:00:34.560049+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `3f319829314500ac13004046836a74c68210dcdb`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.960 | 7.464–11.682 | 58.03 | equal | 6.65× | — | — |
| pipeline_rdfs | 100 | python-reference | 59.608 | 56.228–62.134 | 59.30 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.615 | 17.731–25.670 | 54.64 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 14.968 | 14.412–17.291 | 58.55 | equal | 9.86× | — | — |
| pipeline_owlrl | 100 | python-reference | 147.628 | 140.204–152.908 | 59.38 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 35.217 | 32.685–44.309 | 57.00 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 179.139 | 167.799–242.103 | 110.83 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 643.375 | 603.060–680.722 | 64.84 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 45.174 | 43.742–51.823 | 63.45 | equal | 14.24× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1080.705 | 951.395–1472.547 | 65.84 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 99.862 | 82.740–124.703 | 63.17 | equal | 10.82× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 273.462 | 233.240–346.746 | 120.75 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 21.903 | 20.007–25.033 | 47.66 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.081 | 3.940–5.426 | 55.75 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 43.741 | 32.332–68.879 | 47.33 | reference | — | — | — |
| literal-type | 32 | candidate | 4.808 | 4.555–5.870 | 55.88 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 53.446 | 50.600–69.830 | 47.64 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.960 | 6.310–10.419 | 56.00 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.302 | 8.355–12.136 | 56.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 73.800 | 67.944–81.849 | 47.69 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 22.471 | 18.727–28.094 | 58.56 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 178.111 | 173.695–207.250 | 49.31 | reference | — | — | — |
| literal-type | 512 | python-reference | 307.650 | 245.609–406.207 | 49.58 | reference | — | — | — |
| literal-type | 512 | candidate | 23.109 | 21.455–30.924 | 59.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 397.484 | 334.084–474.081 | 51.52 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 29.971 | 28.224–38.413 | 62.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 517.539 | 452.223–602.616 | 51.70 | reference | — | — | — |
| literal-type | 1000 | candidate | 41.092 | 39.649–67.560 | 62.42 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.5, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
