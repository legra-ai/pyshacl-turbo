# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-22T20:28:19.081184+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `8338e76e5b4e40edca3bbf670d15a1a1edd86fa1`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.156 | 9.009–9.334 | 59.34 | report_graph_equal | — |
| rdfs | 100 | python-reference | 95.736 | 95.480–98.506 | 39.63 | reference | — |
| rdfs | 100 | turbo-historical | 24.597 | 23.580–28.106 | 39.50 | different | — |
| owlrl | 100 | candidate | 12.785 | 12.681–13.021 | 59.84 | report_graph_equal | — |
| owlrl | 100 | python-reference | 224.830 | 221.404–228.198 | 40.02 | reference | — |
| owlrl | 100 | turbo-historical | 38.069 | 37.794–42.059 | 40.84 | different | — |
| rdfs | 1000 | turbo-historical | 242.301 | 238.002–304.025 | 69.17 | different | — |
| rdfs | 1000 | python-reference | 999.819 | 994.671–1081.304 | 47.34 | reference | — |
| rdfs | 1000 | candidate | 75.887 | 75.375–135.364 | 62.43 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1545.565 | 1521.965–1629.590 | 48.69 | reference | — |
| owlrl | 1000 | candidate | 96.360 | 95.732–97.982 | 63.10 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 323.384 | 313.750–329.059 | 75.79 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.1, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
