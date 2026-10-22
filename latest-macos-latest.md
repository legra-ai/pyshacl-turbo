# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-22T21:14:43.068748+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `8338e76e5b4e40edca3bbf670d15a1a1edd86fa1`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.475 | 8.158–10.650 | 55.52 | report_graph_equal | — |
| rdfs | 100 | python-reference | 87.065 | 59.804–112.394 | 47.41 | reference | — |
| rdfs | 100 | turbo-historical | 16.540 | 15.665–19.067 | 47.30 | different | — |
| owlrl | 100 | candidate | 10.611 | 10.302–10.900 | 55.78 | report_graph_equal | — |
| owlrl | 100 | python-reference | 154.295 | 141.636–159.026 | 47.78 | reference | — |
| owlrl | 100 | turbo-historical | 27.497 | 25.209–29.470 | 50.17 | different | — |
| rdfs | 1000 | turbo-historical | 217.439 | 180.498–323.660 | 100.53 | different | — |
| rdfs | 1000 | python-reference | 984.165 | 709.536–1456.486 | 55.23 | reference | — |
| rdfs | 1000 | candidate | 101.109 | 78.263–146.472 | 60.06 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1609.660 | 1419.662–2375.374 | 56.03 | reference | — |
| owlrl | 1000 | candidate | 103.373 | 83.685–111.076 | 60.38 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 266.996 | 261.681–331.855 | 110.06 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.1, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
