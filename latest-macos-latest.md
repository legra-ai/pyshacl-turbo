# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-22T23:53:24.581448+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `b8dc84f8238dc097be5aee2982256072b2ac9b5a`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 8.585 | 7.696–15.399 | 54.58 | report_graph_equal | — |
| rdfs | 100 | python-reference | 63.221 | 58.210–79.363 | 47.52 | reference | — |
| rdfs | 100 | turbo-historical | 28.068 | 24.219–39.367 | 47.73 | different | — |
| owlrl | 100 | candidate | 12.072 | 10.383–13.425 | 54.92 | report_graph_equal | — |
| owlrl | 100 | python-reference | 168.168 | 150.481–180.188 | 47.97 | reference | — |
| owlrl | 100 | turbo-historical | 29.178 | 24.585–36.442 | 50.73 | different | — |
| rdfs | 1000 | turbo-historical | 187.633 | 158.267–241.993 | 104.22 | different | — |
| rdfs | 1000 | python-reference | 737.872 | 725.324–820.410 | 55.34 | reference | — |
| rdfs | 1000 | candidate | 77.612 | 59.764–133.963 | 58.89 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1128.670 | 1024.803–1365.147 | 56.20 | reference | — |
| owlrl | 1000 | candidate | 82.119 | 71.933–90.675 | 59.41 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 304.350 | 272.173–439.579 | 113.67 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.2, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
