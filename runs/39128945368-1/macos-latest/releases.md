# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-18T13:00:10.729943+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `0f7589d318c9eb4201d67ae047b3a06bae3d2695`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 10.543 | 8.404–21.645 | 49.31 | report_graph_equal | — |
| rdfs | 100 | turbo-historical | 25.191 | 17.597–26.128 | 47.69 | different | — |
| rdfs | 100 | python-reference | 120.249 | 77.316–134.787 | 47.42 | reference | — |
| rdfs | 100 | latest-published | 10.576 | 8.140–15.505 | 44.09 | report_graph_equal | — |
| owlrl | 100 | candidate | 19.375 | 14.236–32.228 | 50.34 | report_graph_equal | — |
| owlrl | 100 | python-reference | 240.333 | 157.292–317.548 | 47.81 | reference | — |
| owlrl | 100 | latest-published | 13.977 | 13.278–18.292 | 44.78 | report_graph_equal | — |
| owlrl | 100 | turbo-historical | 31.658 | 29.137–32.547 | 50.30 | different | — |
| rdfs | 1000 | python-reference | 916.254 | 743.666–1012.718 | 55.16 | reference | — |
| rdfs | 1000 | turbo-historical | 284.953 | 206.274–407.849 | 102.67 | different | — |
| rdfs | 1000 | latest-published | 74.090 | 70.642–83.518 | 55.72 | report_graph_equal | — |
| rdfs | 1000 | candidate | 87.185 | 67.824–160.050 | 61.17 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1339.229 | 1171.923–1534.800 | 56.05 | reference | — |
| owlrl | 1000 | latest-published | 146.450 | 132.259–186.574 | 57.17 | report_graph_equal | — |
| owlrl | 1000 | candidate | 163.299 | 131.300–187.205 | 63.31 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 459.759 | 386.989–628.513 | 112.16 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.1, rdflib-turbo 0.2.0a1
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.2, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
