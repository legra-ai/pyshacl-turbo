# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-19T13:35:42.924427+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `69759f81274129edee3d1f6df8a18cf5d005a5c4`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 10.834 | 8.784–17.137 | 49.50 | report_graph_equal | — |
| rdfs | 100 | python-reference | 73.034 | 62.747–96.096 | 47.55 | reference | — |
| rdfs | 100 | turbo-historical | 18.485 | 16.421–28.576 | 47.36 | different | — |
| owlrl | 100 | candidate | 15.954 | 12.990–19.920 | 50.25 | report_graph_equal | — |
| owlrl | 100 | python-reference | 156.454 | 147.060–190.670 | 47.94 | reference | — |
| owlrl | 100 | turbo-historical | 30.502 | 26.922–32.935 | 50.17 | different | — |
| rdfs | 1000 | turbo-historical | 210.801 | 182.608–268.277 | 100.22 | different | — |
| rdfs | 1000 | python-reference | 740.002 | 708.797–804.551 | 55.34 | reference | — |
| rdfs | 1000 | candidate | 72.005 | 63.012–168.573 | 61.20 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1231.100 | 1125.989–1278.331 | 56.12 | reference | — |
| owlrl | 1000 | candidate | 115.879 | 94.331–149.201 | 63.19 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 269.887 | 246.492–326.368 | 109.95 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
