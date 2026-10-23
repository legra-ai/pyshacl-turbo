# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-23T13:55:01.038874+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `f6b6ec015698c324c4a9541463ecb765f2ae0419`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.492 | 7.172–8.315 | 54.66 | report_graph_equal | — |
| rdfs | 100 | python-reference | 77.953 | 62.366–89.061 | 47.39 | reference | — |
| rdfs | 100 | turbo-historical | 27.638 | 20.618–64.133 | 47.12 | different | — |
| owlrl | 100 | candidate | 16.072 | 10.734–310.637 | 54.88 | report_graph_equal | — |
| owlrl | 100 | python-reference | 156.085 | 143.220–213.096 | 47.81 | reference | — |
| owlrl | 100 | turbo-historical | 28.748 | 27.474–33.914 | 50.16 | different | — |
| rdfs | 1000 | turbo-historical | 278.302 | 218.618–323.069 | 99.91 | different | — |
| rdfs | 1000 | python-reference | 803.770 | 682.386–1202.364 | 55.11 | reference | — |
| rdfs | 1000 | candidate | 64.424 | 59.426–111.056 | 58.91 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1070.437 | 1034.550–1620.500 | 55.91 | reference | — |
| owlrl | 1000 | candidate | 72.917 | 69.244–84.917 | 59.27 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 228.127 | 210.650–261.360 | 109.56 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.3, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
