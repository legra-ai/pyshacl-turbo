# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-24T14:47:44.442276+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `454eb25f32b3e1a7474da36d551279bd8f71fd28`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 12.279 | 12.180–12.419 | 53.12 | standard_rdf_equal | — |
| rdfs | 100 | python-reference | 96.445 | 96.264–98.914 | 39.84 | reference | — |
| rdfs | 100 | turbo-historical | 24.182 | 23.822–26.984 | 39.79 | different | — |
| owlrl | 100 | candidate | 13.912 | 13.841–14.111 | 53.95 | standard_rdf_equal | — |
| owlrl | 100 | python-reference | 223.018 | 222.211–227.553 | 40.08 | reference | — |
| owlrl | 100 | turbo-historical | 37.865 | 37.217–40.605 | 41.02 | different | — |
| rdfs | 1000 | turbo-historical | 234.583 | 228.460–288.761 | 69.44 | different | — |
| rdfs | 1000 | python-reference | 991.537 | 987.796–1074.088 | 47.23 | reference | — |
| rdfs | 1000 | candidate | 110.368 | 108.160–110.893 | 56.04 | standard_rdf_equal | — |
| owlrl | 1000 | python-reference | 1545.638 | 1538.057–1659.809 | 48.84 | reference | — |
| owlrl | 1000 | candidate | 99.895 | 98.565–101.863 | 57.27 | standard_rdf_equal | — |
| owlrl | 1000 | turbo-historical | 323.898 | 317.317–334.493 | 76.13 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.5, rdflib-turbo 0.2.0a15

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
