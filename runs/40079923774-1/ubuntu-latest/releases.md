# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-24T09:09:49.722191+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `f6b6ec015698c324c4a9541463ecb765f2ae0419`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.129 | 9.097–9.329 | 57.79 | report_graph_equal | — |
| rdfs | 100 | python-reference | 99.076 | 97.967–114.650 | 39.64 | reference | — |
| rdfs | 100 | turbo-historical | 24.773 | 24.287–27.429 | 39.42 | different | — |
| owlrl | 100 | candidate | 13.116 | 12.873–13.211 | 58.25 | report_graph_equal | — |
| owlrl | 100 | python-reference | 230.449 | 228.961–236.085 | 39.96 | reference | — |
| owlrl | 100 | turbo-historical | 39.112 | 38.508–42.988 | 40.91 | different | — |
| rdfs | 1000 | turbo-historical | 246.969 | 237.130–319.288 | 69.00 | different | — |
| rdfs | 1000 | python-reference | 1014.354 | 1005.558–1145.543 | 47.34 | reference | — |
| rdfs | 1000 | candidate | 78.938 | 76.265–139.147 | 60.94 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1585.681 | 1573.412–1707.737 | 48.69 | reference | — |
| owlrl | 1000 | candidate | 96.784 | 95.784–98.786 | 61.56 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 321.337 | 313.394–324.442 | 75.88 | different | — |
| rdfs | 10000 | turbo-historical | 3497.758 | 3372.100–3680.978 | 390.79 | different | — |
| rdfs | 10000 | python-reference | 26448.374 | 25979.139–27209.119 | 117.83 | reference | — |
| rdfs | 10000 | candidate | 986.988 | 933.191–1035.408 | 91.73 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 15353.466 | 15174.341–15647.472 | 123.38 | reference | — |
| owlrl | 10000 | candidate | 1186.317 | 1150.487–1858.290 | 94.80 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 4776.476 | 4538.835–5337.633 | 450.73 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.3, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
