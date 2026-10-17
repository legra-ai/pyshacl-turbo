# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-17T18:28:36.332709+00:00; platform: macOS-27.0.1-arm64-arm-64bit-Mach-O.
Harness revision: `8c43b9487a0f19db9d42d2af9aa111133efe69d5`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 1000 | candidate | 49.536 | 48.478–86.203 | 64.48 | report_graph_equal | — |
| rdfs | 1000 | turbo-historical | 115.932 | 111.582–152.586 | 105.17 | different | — |
| rdfs | 1000 | python-reference | 474.994 | 451.424–515.071 | 54.91 | reference | — |
| rdfs | 1000 | latest-published | 99.701 | 96.178–145.343 | 102.45 | different | — |
| owlrl | 1000 | candidate | 84.336 | 80.586–91.738 | 77.86 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 741.301 | 698.696–811.838 | 56.09 | reference | — |
| owlrl | 1000 | latest-published | 153.099 | 138.585–164.681 | 113.72 | different | — |
| owlrl | 1000 | turbo-historical | 169.053 | 155.317–187.144 | 113.73 | different | — |
| rdfs | 10000 | python-reference | 11783.553 | 11487.596–12134.901 | 131.53 | reference | — |
| rdfs | 10000 | turbo-historical | 1677.858 | 1468.940–1776.201 | 676.31 | different | — |
| rdfs | 10000 | latest-published | 1699.899 | 1417.556–1751.978 | 637.78 | different | — |
| rdfs | 10000 | candidate | 653.970 | 623.207–1070.852 | 254.50 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 7376.523 | 6848.672–7845.135 | 143.02 | reference | — |
| owlrl | 10000 | latest-published | 2035.550 | 1797.692–2087.804 | 730.20 | different | — |
| owlrl | 10000 | candidate | 951.526 | 932.068–1271.422 | 324.73 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 2226.674 | 2165.724–2265.456 | 780.64 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.3.0, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
