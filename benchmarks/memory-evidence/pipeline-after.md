# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-17T18:35:49.611038+00:00; platform: macOS-27.0.1-arm64-arm-64bit-Mach-O.
Harness revision: `8c43b9487a0f19db9d42d2af9aa111133efe69d5`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 1000 | candidate | 40.038 | 38.994–75.807 | 57.05 | report_graph_equal | — |
| rdfs | 1000 | turbo-historical | 112.162 | 107.277–132.635 | 104.83 | different | — |
| rdfs | 1000 | python-reference | 448.304 | 442.712–472.836 | 54.41 | reference | — |
| rdfs | 1000 | latest-published | 92.809 | 91.729–115.322 | 102.23 | different | — |
| owlrl | 1000 | candidate | 59.369 | 58.703–60.044 | 59.22 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 740.585 | 702.451–845.206 | 56.08 | reference | — |
| owlrl | 1000 | latest-published | 136.892 | 130.787–158.270 | 111.00 | different | — |
| owlrl | 1000 | turbo-historical | 150.900 | 147.672–154.493 | 114.16 | different | — |
| rdfs | 10000 | python-reference | 11787.836 | 11708.418–12121.498 | 135.69 | reference | — |
| rdfs | 10000 | turbo-historical | 1563.108 | 1422.340–1841.989 | 681.91 | different | — |
| rdfs | 10000 | latest-published | 1385.099 | 1226.063–1409.129 | 634.48 | different | — |
| rdfs | 10000 | candidate | 462.431 | 455.109–745.587 | 170.19 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 7339.192 | 7134.726–7736.377 | 142.98 | reference | — |
| owlrl | 10000 | latest-published | 2055.111 | 1878.779–2243.237 | 732.42 | different | — |
| owlrl | 10000 | candidate | 774.907 | 734.023–1315.518 | 197.83 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 2418.278 | 2120.606–2706.049 | 768.38 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.3.0, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
