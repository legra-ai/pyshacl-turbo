# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-23T13:36:46.336587+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `f6b6ec015698c324c4a9541463ecb765f2ae0419`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 10.044 | 8.158–14.169 | 54.58 | report_graph_equal | — |
| rdfs | 100 | python-reference | 61.041 | 59.744–73.616 | 47.52 | reference | — |
| rdfs | 100 | turbo-historical | 19.518 | 18.532–21.572 | 47.64 | different | — |
| owlrl | 100 | candidate | 12.203 | 11.557–14.270 | 54.88 | report_graph_equal | — |
| owlrl | 100 | python-reference | 166.962 | 149.700–193.255 | 47.80 | reference | — |
| owlrl | 100 | turbo-historical | 34.630 | 33.219–42.348 | 50.52 | different | — |
| rdfs | 1000 | turbo-historical | 223.127 | 187.149–257.180 | 104.44 | different | — |
| rdfs | 1000 | python-reference | 850.138 | 716.247–973.668 | 55.28 | reference | — |
| rdfs | 1000 | candidate | 70.491 | 67.211–117.639 | 59.00 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1303.086 | 1155.426–1392.352 | 56.11 | reference | — |
| owlrl | 1000 | candidate | 80.797 | 69.763–98.121 | 59.31 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 238.629 | 215.694–354.856 | 114.16 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.3, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
