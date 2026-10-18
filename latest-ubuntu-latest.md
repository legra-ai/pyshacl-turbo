# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-18T13:01:26.895128+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `0f7589d318c9eb4201d67ae047b3a06bae3d2695`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 10.139 | 9.951–13.503 | 50.89 | report_graph_equal | — |
| rdfs | 100 | turbo-historical | 24.157 | 23.670–28.873 | 39.51 | different | — |
| rdfs | 100 | python-reference | 98.714 | 97.416–102.097 | 39.62 | reference | — |
| rdfs | 100 | latest-published | 9.863 | 9.760–10.633 | 39.67 | report_graph_equal | — |
| owlrl | 100 | candidate | 17.736 | 17.548–17.930 | 51.51 | report_graph_equal | — |
| owlrl | 100 | python-reference | 225.927 | 224.232–231.979 | 40.11 | reference | — |
| owlrl | 100 | latest-published | 16.490 | 16.212–17.015 | 40.39 | report_graph_equal | — |
| owlrl | 100 | turbo-historical | 39.347 | 38.464–43.019 | 40.82 | different | — |
| rdfs | 1000 | python-reference | 1015.429 | 1011.224–1138.641 | 47.28 | reference | — |
| rdfs | 1000 | turbo-historical | 241.913 | 236.338–307.347 | 69.05 | different | — |
| rdfs | 1000 | latest-published | 79.329 | 78.637–82.137 | 47.49 | report_graph_equal | — |
| rdfs | 1000 | candidate | 85.128 | 83.996–155.653 | 58.67 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1573.734 | 1552.967–1655.894 | 48.74 | reference | — |
| owlrl | 1000 | latest-published | 120.995 | 119.850–122.901 | 48.85 | report_graph_equal | — |
| owlrl | 1000 | candidate | 131.154 | 128.844–143.002 | 62.12 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 324.420 | 313.709–340.387 | 75.69 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.1, rdflib-turbo 0.2.0a1
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.2, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
