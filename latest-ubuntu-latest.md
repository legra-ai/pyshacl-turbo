# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-19T10:10:48.790297+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `0bc0212b391c338b30d5f7f47e89fe74caea9203`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 10.025 | 9.914–13.379 | 50.82 | report_graph_equal | — |
| rdfs | 100 | python-reference | 96.374 | 95.752–101.064 | 39.78 | reference | — |
| rdfs | 100 | turbo-historical | 24.587 | 24.157–30.274 | 39.54 | different | — |
| owlrl | 100 | candidate | 17.467 | 17.349–17.744 | 51.53 | report_graph_equal | — |
| owlrl | 100 | python-reference | 225.635 | 223.723–230.565 | 40.10 | reference | — |
| owlrl | 100 | turbo-historical | 38.175 | 37.895–42.141 | 40.90 | different | — |
| rdfs | 1000 | turbo-historical | 239.502 | 231.258–303.405 | 69.11 | different | — |
| rdfs | 1000 | python-reference | 1026.697 | 1004.186–1115.106 | 47.38 | reference | — |
| rdfs | 1000 | candidate | 84.767 | 83.639–169.751 | 58.70 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1570.069 | 1543.708–1669.133 | 48.61 | reference | — |
| owlrl | 1000 | candidate | 130.046 | 126.578–131.173 | 60.88 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 328.421 | 315.107–340.517 | 75.88 | different | — |
| rdfs | 10000 | turbo-historical | 3533.323 | 3472.379–3697.599 | 391.12 | different | — |
| rdfs | 10000 | python-reference | 26546.718 | 25800.180–26734.838 | 117.62 | reference | — |
| rdfs | 10000 | candidate | 1087.087 | 1017.608–1736.977 | 169.37 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 15397.854 | 14986.760–15585.834 | 123.45 | reference | — |
| owlrl | 10000 | candidate | 1543.654 | 1517.752–2350.195 | 163.34 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 4825.016 | 4463.207–5107.286 | 450.70 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
