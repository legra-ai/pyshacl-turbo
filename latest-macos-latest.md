# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-18T15:07:40.303530+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `0bc0212b391c338b30d5f7f47e89fe74caea9203`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 11.595 | 8.722–30.535 | 49.42 | report_graph_equal | — |
| rdfs | 100 | python-reference | 119.634 | 98.415–137.522 | 47.48 | reference | — |
| rdfs | 100 | turbo-historical | 37.463 | 23.272–45.179 | 47.47 | different | — |
| owlrl | 100 | candidate | 25.302 | 20.690–28.677 | 50.33 | report_graph_equal | — |
| owlrl | 100 | python-reference | 333.691 | 249.033–355.442 | 47.83 | reference | — |
| owlrl | 100 | turbo-historical | 50.752 | 43.334–81.513 | 50.53 | different | — |
| rdfs | 1000 | turbo-historical | 271.998 | 250.137–417.535 | 103.36 | different | — |
| rdfs | 1000 | python-reference | 1153.337 | 838.126–1294.747 | 55.19 | reference | — |
| rdfs | 1000 | candidate | 61.697 | 59.842–156.778 | 61.16 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1145.016 | 1047.173–1255.892 | 56.62 | reference | — |
| owlrl | 1000 | candidate | 106.345 | 93.168–115.366 | 63.20 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 261.531 | 217.745–542.713 | 113.58 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
