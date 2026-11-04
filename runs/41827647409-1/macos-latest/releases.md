# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-04T12:40:24.072724+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `b36b227b1766aee5397e3ff30b3076741e5fefdf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.479 | 7.941–12.424 | 59.47 | equal | 7.12× | — | — |
| pipeline_rdfs | 100 | python-reference | 60.381 | 58.187–70.743 | 60.67 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.641 | 21.362–26.774 | 55.95 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 19.548 | 17.663–28.195 | 60.03 | equal | 9.37× | — | — |
| pipeline_owlrl | 100 | python-reference | 183.265 | 168.651–211.300 | 60.92 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 30.811 | 29.537–36.758 | 58.17 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 230.842 | 214.812–310.067 | 111.08 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 781.352 | 664.313–813.748 | 66.20 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 57.867 | 53.721–85.425 | 65.05 | equal | 13.50× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1204.993 | 1007.112–1383.174 | 67.45 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 128.112 | 111.468–158.557 | 64.38 | equal | 9.41× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 301.178 | 273.080–358.948 | 121.16 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3511.378 | 3122.758–3756.592 | 689.89 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 30007.774 | 27678.637–30532.556 | 142.03 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 615.453 | 531.319–776.155 | 129.77 | equal | 48.76× | — | — |
| pipeline_owlrl | 10000 | python-reference | 11986.030 | 11810.707–12345.862 | 151.05 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1332.311 | 1248.759–1893.793 | 122.78 | equal | 9.00× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5656.793 | 5193.258–7133.381 | 782.94 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.175 | 22.140–26.722 | 48.89 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.760 | 4.767–6.514 | 57.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 6.538 | 6.277–7.104 | 57.23 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 31.209 | 27.816–40.116 | 48.95 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.532 | 7.342–10.287 | 57.45 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 62.797 | 57.171–73.632 | 48.91 | reference | — | — | — |
| literal-type | 128 | python-reference | 81.983 | 64.297–109.209 | 48.86 | reference | — | — | — |
| literal-type | 128 | candidate | 11.353 | 10.776–16.918 | 57.45 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 187.364 | 173.926–224.514 | 50.53 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.829 | 19.504–32.648 | 60.05 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 265.926 | 234.750–292.319 | 51.05 | reference | — | — | — |
| literal-type | 512 | candidate | 28.285 | 25.691–32.896 | 60.31 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 34.983 | 33.479–39.625 | 63.38 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 421.305 | 351.401–490.450 | 52.95 | reference | — | — | — |
| literal-type | 1000 | candidate | 48.531 | 45.521–65.153 | 63.73 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 515.661 | 434.307–608.669 | 53.50 | reference | — | — | — |
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
