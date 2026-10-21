# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T22:49:43.575992+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `9fe810ac014092bad5e77e1c6ed0df0d490da4a8`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 6.904 | 6.555–8.029 | 55.55 | report_graph_equal | — |
| rdfs | 100 | python-reference | 67.353 | 54.809–82.144 | 47.56 | reference | — |
| rdfs | 100 | turbo-historical | 15.722 | 15.002–22.645 | 47.56 | different | — |
| owlrl | 100 | candidate | 11.235 | 9.896–11.816 | 55.92 | report_graph_equal | — |
| owlrl | 100 | python-reference | 140.164 | 132.599–186.019 | 47.92 | reference | — |
| owlrl | 100 | turbo-historical | 33.656 | 25.655–42.458 | 50.59 | different | — |
| rdfs | 1000 | turbo-historical | 225.480 | 156.224–240.382 | 104.41 | different | — |
| rdfs | 1000 | python-reference | 702.784 | 647.754–888.476 | 55.38 | reference | — |
| rdfs | 1000 | candidate | 80.694 | 55.604–95.642 | 59.94 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1028.519 | 997.213–1231.212 | 55.91 | reference | — |
| owlrl | 1000 | candidate | 72.494 | 71.448–73.037 | 60.42 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 226.701 | 216.614–269.714 | 114.42 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.0, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
