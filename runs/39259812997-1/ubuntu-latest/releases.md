# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-19T13:47:50.562447+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `3fef1f743bdd05d59f11a19a3c98ea2d30f82b82`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.958 | 7.860–10.971 | 50.75 | report_graph_equal | — |
| rdfs | 100 | python-reference | 75.460 | 74.992–79.969 | 39.77 | reference | — |
| rdfs | 100 | turbo-historical | 19.463 | 19.223–23.750 | 39.52 | different | — |
| owlrl | 100 | candidate | 13.782 | 13.663–13.872 | 51.58 | report_graph_equal | — |
| owlrl | 100 | python-reference | 176.100 | 172.869–180.477 | 40.09 | reference | — |
| owlrl | 100 | turbo-historical | 30.898 | 30.007–33.773 | 40.93 | different | — |
| rdfs | 1000 | turbo-historical | 203.524 | 198.268–279.589 | 69.09 | different | — |
| rdfs | 1000 | python-reference | 775.606 | 767.749–875.400 | 47.29 | reference | — |
| rdfs | 1000 | candidate | 70.072 | 69.030–154.828 | 58.74 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1260.959 | 1215.200–1361.989 | 48.76 | reference | — |
| owlrl | 1000 | candidate | 107.614 | 105.431–112.054 | 61.08 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 283.403 | 278.934–288.633 | 75.87 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
