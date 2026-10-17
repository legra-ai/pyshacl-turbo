# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-17T19:23:44.667752+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `feb2cb0e970bd09cbb131c6ddf96aabbd3f71f05`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.766 | 7.505–13.316 | 45.94 | report_graph_equal | — |
| rdfs | 100 | turbo-historical | 18.162 | 16.768–22.013 | 47.59 | different | — |
| rdfs | 100 | python-reference | 71.679 | 63.702–93.633 | 47.59 | reference | — |
| rdfs | 100 | latest-published | 15.168 | 14.267–19.111 | 48.09 | different | — |
| owlrl | 100 | candidate | 13.345 | 12.777–13.857 | 46.67 | report_graph_equal | — |
| owlrl | 100 | python-reference | 169.550 | 161.268–188.999 | 47.91 | reference | — |
| owlrl | 100 | latest-published | 28.724 | 24.546–33.501 | 50.75 | different | — |
| owlrl | 100 | turbo-historical | 29.484 | 26.458–34.460 | 50.19 | different | — |
| rdfs | 1000 | python-reference | 842.583 | 733.054–1138.782 | 55.44 | reference | — |
| rdfs | 1000 | turbo-historical | 162.459 | 152.022–196.907 | 100.34 | different | — |
| rdfs | 1000 | latest-published | 129.782 | 123.565–171.317 | 102.42 | different | — |
| rdfs | 1000 | candidate | 56.554 | 53.037–110.154 | 57.58 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1096.911 | 993.726–1244.671 | 56.27 | reference | — |
| owlrl | 1000 | latest-published | 207.843 | 195.051–259.630 | 112.09 | different | — |
| owlrl | 1000 | candidate | 93.149 | 81.221–95.531 | 59.62 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 226.669 | 204.603–247.210 | 112.16 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.3.0, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
