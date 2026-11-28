# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T05:45:29.393731+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `0dda2a5678d7863ab07fba7f3b40393295fc13db`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 12.359 | 9.854–17.504 | 58.02 | equal | 6.30× | — | — |
| pipeline_rdfs | 100 | python-reference | 77.901 | 74.782–93.222 | 59.36 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 25.442 | 21.076–33.718 | 54.42 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 19.701 | 18.539–27.081 | 58.61 | equal | 10.54× | — | — |
| pipeline_owlrl | 100 | python-reference | 207.724 | 173.758–231.931 | 59.64 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 44.725 | 38.751–61.270 | 56.48 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 264.703 | 249.506–348.019 | 106.44 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 955.807 | 869.294–1103.048 | 64.97 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 71.117 | 61.140–147.504 | 63.88 | equal | 13.44× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1596.809 | 1205.369–1809.078 | 66.00 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 141.419 | 117.871–173.177 | 63.17 | equal | 11.29× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 435.424 | 304.802–631.412 | 115.47 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 26.977 | 25.737–33.195 | 47.50 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.993 | 4.490–8.047 | 55.75 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 33.962 | 28.384–40.428 | 47.67 | reference | — | — | — |
| literal-type | 32 | candidate | 9.090 | 5.492–11.921 | 55.88 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 69.280 | 64.943–91.670 | 47.55 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.082 | 7.783–9.658 | 56.14 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.212 | 8.214–10.391 | 56.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 87.964 | 71.880–109.263 | 47.66 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 20.337 | 17.075–21.907 | 58.80 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 240.428 | 197.474–254.097 | 49.09 | reference | — | — | — |
| literal-type | 512 | python-reference | 312.673 | 267.079–386.408 | 49.52 | reference | — | — | — |
| literal-type | 512 | candidate | 30.956 | 27.497–38.121 | 59.05 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 562.779 | 483.503–757.195 | 51.50 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 32.629 | 31.537–41.725 | 62.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 718.849 | 644.045–820.091 | 52.06 | reference | — | — | — |
| literal-type | 1000 | candidate | 64.705 | 57.953–68.530 | 62.61 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.7, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
