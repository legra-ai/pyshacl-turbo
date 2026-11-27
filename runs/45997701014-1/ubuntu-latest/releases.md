# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T12:55:55.196941+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `8adb778f823fb5b77c9c45df2ccdd5b3afc802ab`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.719 | 7.663–14.178 | 76.54 | equal | 8.98× | — | — |
| pipeline_rdfs | 100 | python-reference | 69.311 | 68.403–72.382 | 55.52 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.996 | 21.457–26.560 | 54.39 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.532 | 16.248–16.979 | 77.25 | equal | 9.90× | — | — |
| pipeline_owlrl | 100 | python-reference | 163.707 | 162.391–165.719 | 55.87 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.799 | 33.480–37.702 | 54.43 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 225.753 | 218.276–347.624 | 82.43 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 731.951 | 722.231–854.014 | 61.19 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 55.101 | 53.198–56.971 | 80.72 | equal | 13.28× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1139.590 | 1113.231–1248.920 | 62.17 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 101.577 | 101.222–105.063 | 81.26 | equal | 11.22× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 292.312 | 286.951–358.191 | 88.92 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.150 | 23.931–24.475 | 52.50 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.003 | 3.917–4.121 | 74.38 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 28.128 | 27.980–28.605 | 86.25 | reference | — | — | — |
| literal-type | 32 | candidate | 4.485 | 4.365–4.574 | 95.87 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 60.247 | 59.607–60.745 | 120.62 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.706 | 6.592–6.895 | 120.62 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.210 | 8.141–8.448 | 229.06 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 73.893 | 73.278–74.668 | 229.06 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.609 | 17.141–17.747 | 340.42 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 203.612 | 200.258–249.780 | 340.42 | reference | — | — | — |
| literal-type | 512 | python-reference | 257.878 | 253.205–314.562 | 656.50 | reference | — | — | — |
| literal-type | 512 | candidate | 23.412 | 23.230–23.956 | 656.50 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 379.911 | 377.301–466.222 | 1064.75 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 31.386 | 30.844–32.979 | 1064.75 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 500.805 | 492.995–505.029 | 1660.31 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.250 | 42.763–44.571 | 1660.31 | different | — | logical_inplace_owlrl_different | — |
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
