# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T22:18:53.089945+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `2329aa7f82359fda530a9377aa555f84ad76f6de`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.659 | 7.545–7.745 | 59.39 | report_graph_equal | — |
| rdfs | 100 | python-reference | 68.679 | 68.222–72.802 | 39.71 | reference | — |
| rdfs | 100 | turbo-historical | 19.441 | 18.772–24.283 | 39.50 | different | — |
| owlrl | 100 | candidate | 10.576 | 10.507–10.743 | 59.88 | report_graph_equal | — |
| owlrl | 100 | python-reference | 162.527 | 161.103–169.615 | 40.09 | reference | — |
| owlrl | 100 | turbo-historical | 30.316 | 30.074–33.337 | 40.80 | different | — |
| rdfs | 1000 | turbo-historical | 196.306 | 190.143–260.931 | 69.06 | different | — |
| rdfs | 1000 | python-reference | 721.683 | 706.499–821.190 | 47.15 | reference | — |
| rdfs | 1000 | candidate | 65.604 | 64.161–123.358 | 62.43 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1138.090 | 1129.266–1278.672 | 48.81 | reference | — |
| owlrl | 1000 | candidate | 78.948 | 78.377–80.023 | 63.12 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 266.055 | 264.112–272.298 | 75.73 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.0, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
