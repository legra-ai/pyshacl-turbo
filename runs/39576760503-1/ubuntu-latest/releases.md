# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T09:36:21.678620+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `3fef1f743bdd05d59f11a19a3c98ea2d30f82b82`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 10.267 | 9.985–13.570 | 50.69 | report_graph_equal | — |
| rdfs | 100 | python-reference | 97.984 | 96.908–103.105 | 39.62 | reference | — |
| rdfs | 100 | turbo-historical | 25.494 | 25.180–30.475 | 39.41 | different | — |
| owlrl | 100 | candidate | 17.514 | 17.308–18.280 | 51.43 | report_graph_equal | — |
| owlrl | 100 | python-reference | 228.037 | 226.301–238.586 | 40.02 | reference | — |
| owlrl | 100 | turbo-historical | 38.789 | 38.220–42.395 | 40.88 | different | — |
| rdfs | 1000 | turbo-historical | 259.114 | 242.962–323.061 | 69.18 | different | — |
| rdfs | 1000 | python-reference | 1037.701 | 1020.848–1129.990 | 47.23 | reference | — |
| rdfs | 1000 | candidate | 87.772 | 86.361–191.310 | 58.58 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1607.626 | 1582.402–1732.783 | 48.70 | reference | — |
| owlrl | 1000 | candidate | 133.801 | 129.651–137.695 | 60.08 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 358.296 | 352.586–362.099 | 75.80 | different | — |
| rdfs | 10000 | turbo-historical | 3814.766 | 3530.742–3969.538 | 390.71 | different | — |
| rdfs | 10000 | python-reference | 26361.212 | 25726.473–26734.177 | 115.17 | reference | — |
| rdfs | 10000 | candidate | 1146.138 | 1039.768–1677.982 | 170.10 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 15220.220 | 15121.945–15528.780 | 123.38 | reference | — |
| owlrl | 10000 | candidate | 1640.375 | 1630.775–2442.440 | 164.34 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 5104.086 | 4887.243–5478.608 | 449.43 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
