# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-17T17:43:10.268789+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `6d70c357ac40829c5a14bb6c8f68a91c52d68ac8`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 17.580 | 9.548–35.496 | 46.23 | report_graph_equal | — |
| rdfs | 100 | turbo-historical | 31.868 | 28.175–76.552 | 47.16 | different | — |
| rdfs | 100 | python-reference | 106.751 | 82.080–129.162 | 47.38 | reference | — |
| rdfs | 100 | latest-published | 24.584 | 18.599–30.143 | 47.48 | different | — |
| owlrl | 100 | candidate | 33.657 | 24.390–37.704 | 47.58 | report_graph_equal | — |
| owlrl | 100 | python-reference | 221.369 | 186.753–276.935 | 47.75 | reference | — |
| owlrl | 100 | latest-published | 36.204 | 29.666–39.334 | 50.27 | different | — |
| owlrl | 100 | turbo-historical | 44.657 | 35.605–61.131 | 50.06 | different | — |
| rdfs | 1000 | python-reference | 1137.582 | 1030.732–1318.839 | 55.06 | reference | — |
| rdfs | 1000 | turbo-historical | 266.419 | 206.893–413.748 | 102.86 | different | — |
| rdfs | 1000 | latest-published | 203.107 | 156.929–335.190 | 101.53 | different | — |
| rdfs | 1000 | candidate | 97.776 | 85.872–127.883 | 64.56 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1573.563 | 1430.038–1884.960 | 56.03 | reference | — |
| owlrl | 1000 | latest-published | 351.532 | 299.902–513.460 | 111.83 | different | — |
| owlrl | 1000 | candidate | 170.965 | 119.704–190.228 | 75.31 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 380.233 | 328.252–420.214 | 110.20 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.10, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
