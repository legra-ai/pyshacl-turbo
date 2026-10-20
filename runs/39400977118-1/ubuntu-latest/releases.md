# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-20T09:40:28.539694+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `3fef1f743bdd05d59f11a19a3c98ea2d30f82b82`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 10.288 | 10.135–13.903 | 50.70 | report_graph_equal | — |
| rdfs | 100 | python-reference | 98.975 | 97.494–103.543 | 39.65 | reference | — |
| rdfs | 100 | turbo-historical | 24.847 | 24.484–29.917 | 39.43 | different | — |
| owlrl | 100 | candidate | 17.143 | 17.060–17.973 | 51.45 | report_graph_equal | — |
| owlrl | 100 | python-reference | 225.906 | 223.470–230.314 | 40.10 | reference | — |
| owlrl | 100 | turbo-historical | 38.368 | 38.151–41.975 | 40.79 | different | — |
| rdfs | 1000 | turbo-historical | 249.163 | 233.159–306.144 | 69.15 | different | — |
| rdfs | 1000 | python-reference | 1024.540 | 1022.433–1124.037 | 47.26 | reference | — |
| rdfs | 1000 | candidate | 86.038 | 83.825–182.750 | 58.73 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1571.163 | 1557.425–1696.179 | 48.69 | reference | — |
| owlrl | 1000 | candidate | 130.726 | 127.698–133.832 | 60.82 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 329.993 | 320.906–342.059 | 75.77 | different | — |
| rdfs | 10000 | turbo-historical | 3550.710 | 3412.178–3718.402 | 391.53 | different | — |
| rdfs | 10000 | python-reference | 26631.035 | 25992.860–26939.952 | 117.67 | reference | — |
| rdfs | 10000 | candidate | 1048.601 | 1028.140–1593.970 | 167.87 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 15161.670 | 14958.787–15494.967 | 123.16 | reference | — |
| owlrl | 10000 | candidate | 1579.108 | 1554.757–2314.936 | 163.64 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 4929.249 | 4521.380–5045.241 | 451.13 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
