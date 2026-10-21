# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T22:22:20.277448+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `2329aa7f82359fda530a9377aa555f84ad76f6de`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.588 | 7.360–17.668 | 55.72 | report_graph_equal | — |
| rdfs | 100 | python-reference | 62.731 | 59.823–70.994 | 47.52 | reference | — |
| rdfs | 100 | turbo-historical | 19.118 | 16.711–29.748 | 47.69 | different | — |
| owlrl | 100 | candidate | 11.219 | 10.824–21.454 | 55.80 | report_graph_equal | — |
| owlrl | 100 | python-reference | 228.943 | 167.078–245.836 | 47.86 | reference | — |
| owlrl | 100 | turbo-historical | 29.586 | 27.007–43.532 | 50.48 | different | — |
| rdfs | 1000 | turbo-historical | 178.763 | 164.272–251.141 | 103.67 | different | — |
| rdfs | 1000 | python-reference | 676.437 | 629.443–1306.427 | 55.33 | reference | — |
| rdfs | 1000 | candidate | 114.720 | 80.043–169.993 | 60.14 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1636.001 | 1096.360–1943.574 | 56.28 | reference | — |
| owlrl | 1000 | candidate | 79.695 | 76.283–124.042 | 60.39 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 302.024 | 224.942–340.439 | 113.23 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.0, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
