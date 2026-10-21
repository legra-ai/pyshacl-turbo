# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T18:21:57.329839+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `f3344d4202c1c36c62646beb75bfae20fe3ebf95`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 4.739 | 4.687–4.820 | 58.16 | report_graph_equal | — |
| rdfs | 100 | python-reference | 47.808 | 47.365–49.625 | 39.68 | reference | — |
| rdfs | 100 | turbo-historical | 13.865 | 13.552–15.407 | 42.12 | different | — |
| owlrl | 100 | candidate | 7.591 | 7.489–7.616 | 58.49 | report_graph_equal | — |
| owlrl | 100 | python-reference | 116.167 | 114.741–118.036 | 40.03 | reference | — |
| owlrl | 100 | turbo-historical | 21.936 | 21.776–23.686 | 43.36 | different | — |
| rdfs | 1000 | turbo-historical | 138.821 | 134.913–190.477 | 70.93 | different | — |
| rdfs | 1000 | python-reference | 522.449 | 506.523–593.323 | 47.15 | reference | — |
| rdfs | 1000 | candidate | 39.534 | 38.925–39.929 | 61.29 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 853.024 | 815.133–910.184 | 48.65 | reference | — |
| owlrl | 1000 | candidate | 55.690 | 54.777–62.037 | 61.73 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 196.810 | 193.942–201.245 | 77.47 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.5.1, rdflib-turbo 0.2.0a5

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
