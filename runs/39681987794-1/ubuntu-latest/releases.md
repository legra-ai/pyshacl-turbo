# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T22:03:43.570698+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `2329aa7f82359fda530a9377aa555f84ad76f6de`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.369 | 9.352–9.467 | 59.35 | report_graph_equal | — |
| rdfs | 100 | python-reference | 88.143 | 87.750–92.037 | 39.62 | reference | — |
| rdfs | 100 | turbo-historical | 24.200 | 23.998–27.207 | 39.41 | different | — |
| owlrl | 100 | candidate | 13.417 | 13.267–13.521 | 59.88 | report_graph_equal | — |
| owlrl | 100 | python-reference | 209.592 | 207.838–213.939 | 40.01 | reference | — |
| owlrl | 100 | turbo-historical | 37.786 | 37.501–41.619 | 40.81 | different | — |
| rdfs | 1000 | turbo-historical | 238.767 | 231.924–303.018 | 69.13 | different | — |
| rdfs | 1000 | python-reference | 908.733 | 902.961–1017.937 | 47.24 | reference | — |
| rdfs | 1000 | candidate | 82.614 | 81.671–138.512 | 62.28 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1446.953 | 1413.678–1545.431 | 48.72 | reference | — |
| owlrl | 1000 | candidate | 101.303 | 100.223–102.365 | 63.16 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 321.958 | 315.638–328.169 | 75.79 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.0, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
