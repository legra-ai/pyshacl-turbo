# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-21T13:09:04.800849+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 11.248 | 9.147–16.523 | 58.06 | equal | 5.73× | — | — |
| pipeline_rdfs | 100 | python-reference | 64.455 | 61.636–68.408 | 59.33 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.000 | 20.967–36.058 | 54.62 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.566 | 16.598–29.898 | 58.59 | equal | 8.14× | — | — |
| pipeline_owlrl | 100 | python-reference | 142.978 | 141.212–150.134 | 59.66 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 32.610 | 29.520–43.638 | 56.89 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 207.291 | 184.649–279.900 | 109.94 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 662.138 | 637.352–754.284 | 64.80 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 49.903 | 47.492–57.544 | 63.83 | equal | 13.27× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1047.631 | 1016.867–1347.758 | 65.95 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 97.166 | 92.888–137.269 | 63.19 | equal | 10.78× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 290.746 | 261.249–321.547 | 120.38 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3306.342 | 3131.155–4004.494 | 685.22 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 24044.828 | 23587.473–26916.422 | 140.48 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 527.729 | 495.632–985.677 | 129.00 | equal | 45.56× | — | — |
| pipeline_owlrl | 10000 | python-reference | 11026.625 | 10946.851–11845.166 | 149.58 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1116.480 | 976.202–1435.490 | 121.66 | equal | 9.88× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 4553.489 | 4306.547–4754.019 | 785.00 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 22.484 | 21.812–24.986 | 47.55 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.180 | 4.099–4.353 | 55.78 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.698 | 4.639–6.017 | 55.83 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 34.896 | 24.831–55.623 | 47.55 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.897 | 6.607–9.849 | 56.11 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 59.171 | 50.518–71.459 | 47.52 | reference | — | — | — |
| literal-type | 128 | python-reference | 70.429 | 64.567–76.257 | 47.52 | reference | — | — | — |
| literal-type | 128 | candidate | 8.442 | 8.225–10.075 | 56.20 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 210.390 | 176.942–245.747 | 49.14 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.254 | 16.032–17.456 | 58.67 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 261.367 | 228.628–298.573 | 49.41 | reference | — | — | — |
| literal-type | 512 | candidate | 23.841 | 21.544–35.179 | 58.98 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 31.326 | 29.716–35.365 | 62.02 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 393.341 | 357.705–433.659 | 51.36 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.935 | 38.993–48.131 | 62.55 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 450.381 | 437.254–512.249 | 51.95 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
