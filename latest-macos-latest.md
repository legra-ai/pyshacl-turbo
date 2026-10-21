# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T18:09:21.052325+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `e22452a995d1aa2e990a92d43d5ff63d60dc3cc2`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.741 | 7.567–10.279 | 48.41 | report_graph_equal | — |
| rdfs | 100 | python-reference | 65.550 | 57.746–66.259 | 47.41 | reference | — |
| rdfs | 100 | turbo-historical | 18.295 | 18.003–20.631 | 47.56 | different | — |
| owlrl | 100 | candidate | 11.902 | 11.530–12.334 | 48.84 | report_graph_equal | — |
| owlrl | 100 | python-reference | 148.436 | 147.158–151.168 | 48.05 | reference | — |
| owlrl | 100 | turbo-historical | 28.028 | 25.186–31.071 | 50.39 | different | — |
| rdfs | 1000 | turbo-historical | 165.523 | 160.639–212.106 | 102.95 | different | — |
| rdfs | 1000 | python-reference | 674.451 | 655.917–721.126 | 55.30 | reference | — |
| rdfs | 1000 | candidate | 64.337 | 61.947–117.344 | 53.38 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1027.476 | 966.257–1100.427 | 56.06 | reference | — |
| owlrl | 1000 | candidate | 77.899 | 75.408–79.633 | 54.39 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 232.790 | 203.476–288.635 | 111.22 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.5.0, rdflib-turbo 0.2.0a5

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
