# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-19T13:48:50.844280+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `3fef1f743bdd05d59f11a19a3c98ea2d30f82b82`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.631 | 9.001–12.831 | 49.61 | report_graph_equal | — |
| rdfs | 100 | python-reference | 87.605 | 59.989–114.867 | 47.64 | reference | — |
| rdfs | 100 | turbo-historical | 30.870 | 21.177–40.499 | 47.83 | different | — |
| owlrl | 100 | candidate | 16.119 | 13.073–30.987 | 50.50 | report_graph_equal | — |
| owlrl | 100 | python-reference | 216.373 | 185.744–236.787 | 48.02 | reference | — |
| owlrl | 100 | turbo-historical | 34.565 | 32.209–58.029 | 50.58 | different | — |
| rdfs | 1000 | turbo-historical | 237.166 | 202.249–261.774 | 104.20 | different | — |
| rdfs | 1000 | python-reference | 896.936 | 763.846–1082.861 | 55.30 | reference | — |
| rdfs | 1000 | candidate | 81.246 | 77.745–159.959 | 61.19 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1312.413 | 1143.605–1557.368 | 56.14 | reference | — |
| owlrl | 1000 | candidate | 106.712 | 97.904–127.295 | 63.14 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 292.232 | 272.607–302.653 | 113.39 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
