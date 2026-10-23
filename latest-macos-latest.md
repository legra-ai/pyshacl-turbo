# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-23T13:03:37.585950+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `ef864131457da8cea9cb89044ed87d4e1bf130d3`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 11.089 | 9.998–17.990 | 54.59 | report_graph_equal | — |
| rdfs | 100 | python-reference | 117.984 | 89.331–133.597 | 47.47 | reference | — |
| rdfs | 100 | turbo-historical | 38.202 | 30.462–50.093 | 47.36 | different | — |
| owlrl | 100 | candidate | 20.774 | 14.643–34.511 | 54.92 | report_graph_equal | — |
| owlrl | 100 | python-reference | 290.412 | 267.447–308.885 | 47.97 | reference | — |
| owlrl | 100 | turbo-historical | 42.361 | 37.759–54.056 | 50.03 | different | — |
| rdfs | 1000 | turbo-historical | 268.775 | 209.322–314.371 | 103.61 | different | — |
| rdfs | 1000 | python-reference | 773.493 | 723.178–890.209 | 55.28 | reference | — |
| rdfs | 1000 | candidate | 67.106 | 61.535–102.365 | 58.97 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1189.813 | 1074.294–1373.537 | 56.30 | reference | — |
| owlrl | 1000 | candidate | 88.198 | 78.142–134.295 | 59.36 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 369.323 | 279.662–526.773 | 109.78 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.2, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
