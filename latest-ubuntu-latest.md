# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-19T13:29:25.286125+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `69759f81274129edee3d1f6df8a18cf5d005a5c4`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.845 | 9.642–13.298 | 50.68 | report_graph_equal | — |
| rdfs | 100 | python-reference | 95.987 | 95.536–98.477 | 39.63 | reference | — |
| rdfs | 100 | turbo-historical | 24.812 | 23.773–29.744 | 39.45 | different | — |
| owlrl | 100 | candidate | 16.881 | 16.773–17.092 | 51.45 | report_graph_equal | — |
| owlrl | 100 | python-reference | 227.149 | 224.520–231.175 | 40.13 | reference | — |
| owlrl | 100 | turbo-historical | 37.798 | 37.014–40.780 | 40.79 | different | — |
| rdfs | 1000 | turbo-historical | 235.273 | 228.157–290.492 | 69.03 | different | — |
| rdfs | 1000 | python-reference | 991.611 | 981.563–1068.018 | 47.38 | reference | — |
| rdfs | 1000 | candidate | 84.049 | 83.644–158.962 | 58.62 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1539.118 | 1522.019–1634.992 | 48.72 | reference | — |
| owlrl | 1000 | candidate | 127.150 | 126.016–128.377 | 60.02 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 312.770 | 309.053–320.326 | 75.86 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
