# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-03T19:36:38.208483+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `8f03cd4296b36764950306219408eefd65624b28`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.032 | 6.613–9.220 | 59.45 | equal | 12.35× | — | — |
| pipeline_rdfs | 100 | python-reference | 86.827 | 57.998–105.473 | 60.77 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 18.841 | 18.318–21.279 | 55.83 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.240 | 17.036–19.347 | 59.91 | equal | 9.10× | — | — |
| pipeline_owlrl | 100 | python-reference | 156.841 | 142.557–171.093 | 61.08 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 33.856 | 32.559–35.675 | 58.16 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 319.241 | 220.090–511.954 | 111.55 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 687.505 | 664.772–811.412 | 66.31 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 51.887 | 50.218–66.366 | 65.17 | equal | 13.25× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1135.364 | 1063.045–1315.185 | 67.39 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 119.041 | 110.564–141.748 | 64.38 | equal | 9.54× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 298.746 | 248.534–328.068 | 121.61 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 23.130 | 22.122–24.251 | 48.94 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.532 | 4.106–4.795 | 57.02 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.974 | 26.078–35.178 | 49.03 | reference | — | — | — |
| literal-type | 32 | candidate | 5.533 | 5.350–6.146 | 57.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 53.573 | 50.947–70.792 | 48.98 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.861 | 8.080–11.852 | 57.39 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.400 | 8.950–10.058 | 57.47 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 69.958 | 62.181–75.007 | 48.92 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.137 | 18.784–23.377 | 59.97 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 187.690 | 180.018–256.210 | 50.58 | reference | — | — | — |
| literal-type | 512 | python-reference | 240.670 | 229.290–267.934 | 50.91 | reference | — | — | — |
| literal-type | 512 | candidate | 25.451 | 24.770–27.919 | 60.33 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 421.951 | 358.354–600.625 | 52.83 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 35.052 | 32.826–40.787 | 63.28 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 522.062 | 463.728–591.053 | 53.39 | reference | — | — | — |
| literal-type | 1000 | candidate | 48.810 | 48.247–77.342 | 63.84 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.9.1, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
