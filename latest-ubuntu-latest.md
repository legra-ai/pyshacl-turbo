# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-22T17:21:20.272596+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `576afa30e7fa8bc0c446b1e871bc75c0590a2b33`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.205 | 9.180–9.341 | 59.40 | report_graph_equal | — |
| rdfs | 100 | python-reference | 97.568 | 97.032–101.490 | 39.73 | reference | — |
| rdfs | 100 | turbo-historical | 24.975 | 24.617–30.963 | 39.45 | different | — |
| owlrl | 100 | candidate | 13.124 | 12.894–13.267 | 59.85 | report_graph_equal | — |
| owlrl | 100 | python-reference | 227.877 | 226.270–233.245 | 40.10 | reference | — |
| owlrl | 100 | turbo-historical | 39.494 | 39.013–43.534 | 40.84 | different | — |
| rdfs | 1000 | turbo-historical | 247.875 | 240.169–308.951 | 69.14 | different | — |
| rdfs | 1000 | python-reference | 1026.260 | 1012.346–1123.987 | 47.14 | reference | — |
| rdfs | 1000 | candidate | 79.299 | 77.753–137.706 | 62.51 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1578.703 | 1563.133–1702.116 | 48.69 | reference | — |
| owlrl | 1000 | candidate | 95.802 | 94.334–96.961 | 63.30 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 328.773 | 315.394–337.266 | 75.71 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.0, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
