# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-22T23:06:55.367432+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `b8dc84f8238dc097be5aee2982256072b2ac9b5a`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.289 | 9.243–9.372 | 57.81 | report_graph_equal | — |
| rdfs | 100 | python-reference | 88.020 | 86.933–91.969 | 39.72 | reference | — |
| rdfs | 100 | turbo-historical | 24.157 | 23.793–29.075 | 39.43 | different | — |
| owlrl | 100 | candidate | 13.265 | 13.184–14.060 | 58.23 | report_graph_equal | — |
| owlrl | 100 | python-reference | 207.311 | 205.665–212.304 | 40.01 | reference | — |
| owlrl | 100 | turbo-historical | 37.683 | 37.522–41.236 | 40.80 | different | — |
| rdfs | 1000 | turbo-historical | 236.882 | 229.264–297.389 | 69.09 | different | — |
| rdfs | 1000 | python-reference | 900.727 | 887.012–983.988 | 47.15 | reference | — |
| rdfs | 1000 | candidate | 82.747 | 81.687–134.424 | 60.81 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1436.431 | 1417.782–1544.579 | 48.71 | reference | — |
| owlrl | 1000 | candidate | 99.818 | 98.729–101.366 | 61.65 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 321.278 | 318.194–324.172 | 75.85 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.2, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
