# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T20:29:26.100037+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `f3344d4202c1c36c62646beb75bfae20fe3ebf95`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 4.718 | 4.656–4.776 | 51.57 | report_graph_equal | — |
| rdfs | 100 | python-reference | 48.373 | 47.507–51.148 | 39.69 | reference | — |
| rdfs | 100 | turbo-historical | 13.338 | 13.176–14.598 | 39.49 | different | — |
| owlrl | 100 | candidate | 7.768 | 7.534–7.905 | 52.17 | report_graph_equal | — |
| owlrl | 100 | python-reference | 113.052 | 111.674–115.626 | 40.04 | reference | — |
| owlrl | 100 | turbo-historical | 22.703 | 21.756–25.592 | 40.94 | different | — |
| rdfs | 1000 | turbo-historical | 144.018 | 136.333–189.662 | 69.09 | different | — |
| rdfs | 1000 | python-reference | 525.199 | 493.137–685.582 | 47.23 | reference | — |
| rdfs | 1000 | candidate | 42.785 | 41.714–44.203 | 54.60 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 863.324 | 801.338–988.115 | 48.81 | reference | — |
| owlrl | 1000 | candidate | 59.324 | 56.243–59.842 | 55.35 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 224.882 | 217.444–230.171 | 75.71 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.5.1, rdflib-turbo 0.2.0a5

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
