# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-06T12:25:49.213965+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `bc9ec2d32b8345fcaf7a4f0aaac62f273cce658e`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.871 | 7.641–12.257 | 68.84 | equal | 12.19× | — | — |
| pipeline_rdfs | 100 | python-reference | 95.972 | 94.162–107.780 | 48.41 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 25.976 | 25.313–30.884 | 46.64 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.544 | 18.325–18.828 | 69.39 | equal | 12.23× | — | — |
| pipeline_owlrl | 100 | python-reference | 226.837 | 222.760–228.787 | 48.65 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 38.905 | 37.942–41.332 | 46.80 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 263.840 | 254.491–396.436 | 74.57 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 944.140 | 929.066–1043.850 | 53.21 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 56.640 | 55.664–58.696 | 72.00 | equal | 16.67× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1574.200 | 1567.720–1677.980 | 54.64 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 114.500 | 114.206–116.814 | 72.52 | equal | 13.75× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 329.043 | 323.885–428.300 | 81.15 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3917.969 | 3546.978–4048.656 | 392.77 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 21608.041 | 21527.900–21841.505 | 119.48 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 773.860 | 733.117–1273.557 | 116.03 | equal | 27.92× | — | — |
| pipeline_owlrl | 10000 | python-reference | 15847.218 | 15728.978–16032.695 | 127.88 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1311.757 | 1277.338–1829.142 | 116.87 | equal | 12.08× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5526.233 | 5211.052–5777.418 | 452.74 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 34.966 | 34.403–36.519 | 153.93 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.374 | 4.289–4.417 | 153.93 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.806 | 4.757–4.881 | 186.80 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 42.807 | 42.308–43.317 | 186.80 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.524 | 7.462–7.643 | 225.50 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 85.848 | 84.892–107.224 | 225.50 | reference | — | — | — |
| literal-type | 128 | python-reference | 107.678 | 106.486–108.462 | 314.11 | reference | — | — | — |
| literal-type | 128 | candidate | 9.068 | 9.022–9.183 | 314.11 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 289.438 | 283.911–321.323 | 424.91 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.479 | 19.146–19.725 | 424.91 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 379.610 | 369.825–416.246 | 742.62 | reference | — | — | — |
| literal-type | 512 | candidate | 26.254 | 26.082–30.981 | 742.62 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 35.140 | 34.612–38.608 | 1150.78 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 539.486 | 533.625–642.236 | 1150.78 | reference | — | — | — |
| literal-type | 1000 | candidate | 48.667 | 48.110–49.512 | 1749.87 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 720.424 | 711.476–728.499 | 1749.87 | reference | — | — | — |
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
