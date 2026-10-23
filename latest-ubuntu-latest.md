# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-23T13:00:58.666067+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `ef864131457da8cea9cb89044ed87d4e1bf130d3`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.008 | 8.932–9.089 | 57.78 | report_graph_equal | — |
| rdfs | 100 | python-reference | 96.411 | 95.578–99.553 | 39.72 | reference | — |
| rdfs | 100 | turbo-historical | 24.350 | 24.020–30.039 | 39.46 | different | — |
| owlrl | 100 | candidate | 12.856 | 12.730–12.958 | 58.30 | report_graph_equal | — |
| owlrl | 100 | python-reference | 225.110 | 222.689–228.275 | 40.00 | reference | — |
| owlrl | 100 | turbo-historical | 37.712 | 37.142–41.290 | 40.80 | different | — |
| rdfs | 1000 | turbo-historical | 235.945 | 228.478–295.577 | 69.11 | different | — |
| rdfs | 1000 | python-reference | 999.492 | 993.881–1075.084 | 47.34 | reference | — |
| rdfs | 1000 | candidate | 77.597 | 76.473–125.942 | 60.59 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1542.048 | 1526.469–1646.291 | 48.73 | reference | — |
| owlrl | 1000 | candidate | 97.921 | 97.001–101.048 | 61.57 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 319.803 | 311.195–334.423 | 75.73 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.2, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
