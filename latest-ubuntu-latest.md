# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T16:54:04.574285+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `e22452a995d1aa2e990a92d43d5ff63d60dc3cc2`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.078 | 8.916–13.202 | 57.36 | report_graph_equal | — |
| rdfs | 100 | python-reference | 93.076 | 90.772–96.401 | 39.75 | reference | — |
| rdfs | 100 | turbo-historical | 23.763 | 23.272–29.190 | 39.30 | different | — |
| owlrl | 100 | candidate | 13.648 | 13.539–13.805 | 57.77 | report_graph_equal | — |
| owlrl | 100 | python-reference | 214.908 | 211.439–219.013 | 40.12 | reference | — |
| owlrl | 100 | turbo-historical | 37.392 | 36.849–42.233 | 40.83 | different | — |
| rdfs | 1000 | turbo-historical | 241.688 | 234.398–312.358 | 69.23 | different | — |
| rdfs | 1000 | python-reference | 954.808 | 950.040–1052.202 | 47.13 | reference | — |
| rdfs | 1000 | candidate | 76.291 | 74.088–183.196 | 61.11 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1489.882 | 1469.029–1629.903 | 48.68 | reference | — |
| owlrl | 1000 | candidate | 98.469 | 97.933–101.574 | 61.80 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 339.654 | 336.731–351.279 | 75.79 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.5.0, rdflib-turbo 0.2.0a5

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
