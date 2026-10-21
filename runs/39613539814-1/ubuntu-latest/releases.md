# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T14:17:48.910789+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `f1a7d3ba9dee70d6ce95b75836dc8f511e03627c`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 8.813 | 8.723–13.099 | 57.10 | report_graph_equal | — |
| rdfs | 100 | python-reference | 87.235 | 86.977–91.979 | 39.77 | reference | — |
| rdfs | 100 | turbo-historical | 23.221 | 22.621–28.737 | 42.14 | different | — |
| owlrl | 100 | candidate | 13.292 | 13.107–13.530 | 57.43 | report_graph_equal | — |
| owlrl | 100 | python-reference | 205.023 | 203.181–228.480 | 40.14 | reference | — |
| owlrl | 100 | turbo-historical | 36.195 | 35.684–40.585 | 43.48 | different | — |
| rdfs | 1000 | turbo-historical | 235.004 | 230.909–313.195 | 71.08 | different | — |
| rdfs | 1000 | python-reference | 922.398 | 916.634–1024.062 | 47.47 | reference | — |
| rdfs | 1000 | candidate | 74.487 | 73.923–164.316 | 60.80 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1448.074 | 1438.538–1557.392 | 48.71 | reference | — |
| owlrl | 1000 | candidate | 99.604 | 98.443–101.440 | 61.45 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 330.809 | 326.489–334.420 | 77.57 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.5.0, rdflib-turbo 0.2.0a5

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
