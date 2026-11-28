# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T05:40:13.856819+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `0dda2a5678d7863ab07fba7f3b40393295fc13db`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.210 | 8.982–12.927 | 76.70 | equal | 10.44× | — | — |
| pipeline_rdfs | 100 | python-reference | 96.107 | 95.786–98.630 | 55.71 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.500 | 27.006–32.095 | 54.04 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.612 | 20.185–20.838 | 77.41 | equal | 10.79× | — | — |
| pipeline_owlrl | 100 | python-reference | 222.309 | 220.612–225.188 | 55.89 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 42.661 | 41.514–45.160 | 54.24 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 273.377 | 266.112–355.356 | 82.44 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1022.369 | 1004.102–1124.493 | 61.17 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 67.897 | 65.464–70.900 | 80.83 | equal | 15.06× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1562.476 | 1544.137–1638.871 | 62.17 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 124.011 | 123.615–126.059 | 81.41 | equal | 12.60× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 366.115 | 360.691–448.322 | 88.81 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.053 | 31.735–32.539 | 52.43 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.939 | 4.858–5.296 | 74.36 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 37.965 | 37.493–38.371 | 86.31 | reference | — | — | — |
| literal-type | 32 | candidate | 5.431 | 5.348–5.502 | 95.81 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 79.930 | 79.279–80.762 | 120.68 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.190 | 8.013–8.418 | 120.68 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.164 | 9.980–10.309 | 229.00 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 100.768 | 99.729–101.185 | 229.00 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.105 | 20.871–21.593 | 340.18 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 274.434 | 272.750–300.650 | 340.18 | reference | — | — | — |
| literal-type | 512 | python-reference | 353.089 | 350.821–386.602 | 656.39 | reference | — | — | — |
| literal-type | 512 | candidate | 28.905 | 28.347–29.144 | 656.39 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 525.283 | 521.445–619.184 | 1064.63 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 38.317 | 37.931–39.269 | 1064.63 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 676.924 | 671.253–697.049 | 1660.14 | reference | — | — | — |
| literal-type | 1000 | candidate | 52.785 | 51.725–54.590 | 1660.14 | different | — | logical_inplace_owlrl_different | — |
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
