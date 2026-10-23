# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-23T09:36:57.851016+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `b8dc84f8238dc097be5aee2982256072b2ac9b5a`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 8.796 | 8.771–8.843 | 57.79 | report_graph_equal | — |
| rdfs | 100 | python-reference | 95.870 | 95.496–99.172 | 39.72 | reference | — |
| rdfs | 100 | turbo-historical | 24.349 | 23.777–28.778 | 39.45 | different | — |
| owlrl | 100 | candidate | 12.517 | 12.431–12.858 | 58.21 | report_graph_equal | — |
| owlrl | 100 | python-reference | 223.695 | 220.312–227.086 | 40.00 | reference | — |
| owlrl | 100 | turbo-historical | 37.679 | 37.245–40.801 | 40.81 | different | — |
| rdfs | 1000 | turbo-historical | 232.801 | 227.398–287.975 | 69.08 | different | — |
| rdfs | 1000 | python-reference | 997.292 | 987.416–1076.645 | 47.47 | reference | — |
| rdfs | 1000 | candidate | 77.369 | 76.609–127.995 | 60.71 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1543.499 | 1524.781–1645.026 | 48.73 | reference | — |
| owlrl | 1000 | candidate | 95.318 | 94.530–96.749 | 61.50 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 318.545 | 310.991–326.540 | 75.71 | different | — |
| rdfs | 10000 | turbo-historical | 3355.459 | 3059.292–3421.888 | 391.06 | different | — |
| rdfs | 10000 | python-reference | 26076.839 | 25759.123–26209.565 | 115.10 | reference | — |
| rdfs | 10000 | candidate | 857.237 | 833.951–887.066 | 91.98 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 14882.335 | 14780.143–14905.365 | 123.16 | reference | — |
| owlrl | 10000 | candidate | 1085.049 | 1074.580–1654.903 | 94.84 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 4757.295 | 4716.262–4943.476 | 450.09 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.2, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
