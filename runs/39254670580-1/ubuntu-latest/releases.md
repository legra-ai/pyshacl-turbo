# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-19T12:57:37.102140+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `7f7516b97c3a7fb3ac0cf03bfec7c83ffa8e7539`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 10.102 | 9.993–13.646 | 50.83 | report_graph_equal | — |
| rdfs | 100 | python-reference | 96.800 | 95.950–98.868 | 39.63 | reference | — |
| rdfs | 100 | turbo-historical | 24.745 | 24.228–27.312 | 39.41 | different | — |
| owlrl | 100 | candidate | 17.419 | 17.195–17.764 | 51.43 | report_graph_equal | — |
| owlrl | 100 | python-reference | 226.776 | 225.512–232.919 | 40.15 | reference | — |
| owlrl | 100 | turbo-historical | 38.255 | 38.009–42.161 | 40.93 | different | — |
| rdfs | 1000 | turbo-historical | 245.267 | 237.685–312.898 | 69.09 | different | — |
| rdfs | 1000 | python-reference | 1024.212 | 1010.991–1117.174 | 47.12 | reference | — |
| rdfs | 1000 | candidate | 86.113 | 84.665–194.597 | 58.67 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1599.202 | 1588.605–1708.246 | 48.66 | reference | — |
| owlrl | 1000 | candidate | 131.648 | 127.503–136.576 | 60.80 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 344.661 | 338.178–351.812 | 75.75 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
