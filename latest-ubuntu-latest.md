# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-24T15:26:41.069185+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `14a6f3b3f518b4fe25d6463246d38042ab143e14`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.365 | 7.205–7.446 | 53.18 | standard_rdf_equal | — |
| rdfs | 100 | python-reference | 47.884 | 47.080–49.894 | 39.72 | reference | — |
| rdfs | 100 | turbo-historical | 13.610 | 13.280–15.239 | 39.72 | different | — |
| owlrl | 100 | candidate | 8.144 | 8.037–8.349 | 53.99 | standard_rdf_equal | — |
| owlrl | 100 | python-reference | 115.156 | 110.677–122.301 | 40.19 | reference | — |
| owlrl | 100 | turbo-historical | 21.302 | 20.838–23.056 | 40.92 | different | — |
| rdfs | 1000 | turbo-historical | 134.171 | 128.600–181.368 | 69.42 | different | — |
| rdfs | 1000 | python-reference | 492.867 | 484.182–615.848 | 47.22 | reference | — |
| rdfs | 1000 | candidate | 65.404 | 63.104–67.728 | 56.08 | standard_rdf_equal | — |
| owlrl | 1000 | python-reference | 787.535 | 766.066–875.441 | 48.81 | reference | — |
| owlrl | 1000 | candidate | 55.643 | 53.376–66.858 | 57.27 | standard_rdf_equal | — |
| owlrl | 1000 | turbo-historical | 184.082 | 182.846–218.956 | 75.96 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.5, rdflib-turbo 0.2.0a15

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
