# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-22T23:39:23.846598+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `b8dc84f8238dc097be5aee2982256072b2ac9b5a`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 5.325 | 5.268–5.345 | 57.71 | report_graph_equal | — |
| rdfs | 100 | python-reference | 49.764 | 47.370–51.536 | 39.68 | reference | — |
| rdfs | 100 | turbo-historical | 13.776 | 13.217–15.839 | 39.50 | different | — |
| owlrl | 100 | candidate | 7.385 | 7.288–7.865 | 58.29 | report_graph_equal | — |
| owlrl | 100 | python-reference | 118.767 | 116.390–120.383 | 40.06 | reference | — |
| owlrl | 100 | turbo-historical | 22.201 | 21.756–24.088 | 40.90 | different | — |
| rdfs | 1000 | turbo-historical | 151.626 | 143.130–238.051 | 69.18 | different | — |
| rdfs | 1000 | python-reference | 547.884 | 495.853–596.066 | 47.47 | reference | — |
| rdfs | 1000 | candidate | 46.716 | 46.031–102.192 | 60.86 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 784.963 | 766.896–888.590 | 48.67 | reference | — |
| owlrl | 1000 | candidate | 53.528 | 52.704–54.457 | 61.65 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 183.663 | 178.817–201.852 | 75.74 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.2, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
