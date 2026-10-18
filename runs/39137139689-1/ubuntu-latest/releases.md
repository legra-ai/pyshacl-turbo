# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-18T14:53:39.282260+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `0bc0212b391c338b30d5f7f47e89fe74caea9203`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 10.498 | 10.247–15.963 | 50.81 | report_graph_equal | — |
| rdfs | 100 | python-reference | 99.609 | 97.951–104.474 | 39.74 | reference | — |
| rdfs | 100 | turbo-historical | 26.974 | 26.350–34.545 | 39.50 | different | — |
| owlrl | 100 | candidate | 18.372 | 18.129–19.119 | 51.43 | report_graph_equal | — |
| owlrl | 100 | python-reference | 231.763 | 228.318–238.205 | 40.00 | reference | — |
| owlrl | 100 | turbo-historical | 39.727 | 39.409–44.213 | 40.94 | different | — |
| rdfs | 1000 | turbo-historical | 257.608 | 245.304–325.210 | 69.15 | different | — |
| rdfs | 1000 | python-reference | 1032.620 | 1027.941–1146.369 | 47.13 | reference | — |
| rdfs | 1000 | candidate | 92.000 | 90.009–198.749 | 58.64 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1622.008 | 1601.850–1731.511 | 48.68 | reference | — |
| owlrl | 1000 | candidate | 144.085 | 135.811–146.231 | 60.09 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 358.147 | 352.430–364.522 | 75.83 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
