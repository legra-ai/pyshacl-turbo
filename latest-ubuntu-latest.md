# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-24T13:17:36.699036+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `8042927fcdaddd82c166cff2e8c103c944256135`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 12.245 | 12.115–12.544 | 53.02 | standard_rdf_equal | — |
| rdfs | 100 | python-reference | 96.953 | 96.756–100.432 | 39.65 | reference | — |
| rdfs | 100 | turbo-historical | 24.164 | 23.859–28.298 | 39.45 | different | — |
| owlrl | 100 | candidate | 14.088 | 14.038–14.203 | 53.84 | standard_rdf_equal | — |
| owlrl | 100 | python-reference | 230.044 | 225.271–231.688 | 40.00 | reference | — |
| owlrl | 100 | turbo-historical | 38.513 | 38.130–41.975 | 40.80 | different | — |
| rdfs | 1000 | turbo-historical | 242.272 | 236.570–299.157 | 69.20 | different | — |
| rdfs | 1000 | python-reference | 998.123 | 994.106–1081.301 | 47.14 | reference | — |
| rdfs | 1000 | candidate | 108.291 | 107.046–109.835 | 55.96 | standard_rdf_equal | — |
| owlrl | 1000 | python-reference | 1578.046 | 1555.050–1642.735 | 48.72 | reference | — |
| owlrl | 1000 | candidate | 96.535 | 96.042–100.114 | 57.09 | standard_rdf_equal | — |
| owlrl | 1000 | turbo-historical | 320.690 | 313.576–324.538 | 75.80 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.4, rdflib-turbo 0.2.0a15

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
