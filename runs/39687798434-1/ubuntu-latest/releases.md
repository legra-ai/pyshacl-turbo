# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T22:47:12.171351+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `9fe810ac014092bad5e77e1c6ed0df0d490da4a8`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 5.745 | 5.645–6.053 | 65.62 | report_graph_equal | — |
| rdfs | 100 | python-reference | 50.186 | 49.764–53.312 | 39.71 | reference | — |
| rdfs | 100 | turbo-historical | 14.152 | 13.946–15.945 | 39.41 | different | — |
| owlrl | 100 | candidate | 7.989 | 7.805–8.135 | 65.98 | report_graph_equal | — |
| owlrl | 100 | python-reference | 118.440 | 115.930–138.182 | 40.08 | reference | — |
| owlrl | 100 | turbo-historical | 22.626 | 22.165–24.172 | 40.77 | different | — |
| rdfs | 1000 | turbo-historical | 143.730 | 140.601–216.791 | 69.21 | different | — |
| rdfs | 1000 | python-reference | 522.491 | 510.928–616.445 | 47.15 | reference | — |
| rdfs | 1000 | candidate | 47.623 | 47.170–98.289 | 68.66 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 801.314 | 783.659–910.120 | 48.69 | reference | — |
| owlrl | 1000 | candidate | 56.420 | 55.090–59.017 | 69.29 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 198.978 | 195.238–214.123 | 75.67 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.0, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
