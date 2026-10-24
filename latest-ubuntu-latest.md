# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-24T14:25:51.032049+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `454eb25f32b3e1a7474da36d551279bd8f71fd28`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 11.108 | 11.037–11.161 | 53.16 | standard_rdf_equal | — |
| rdfs | 100 | python-reference | 87.934 | 87.181–91.481 | 39.80 | reference | — |
| rdfs | 100 | turbo-historical | 22.828 | 22.633–28.597 | 39.88 | different | — |
| owlrl | 100 | candidate | 13.062 | 12.910–13.170 | 54.05 | standard_rdf_equal | — |
| owlrl | 100 | python-reference | 207.767 | 205.861–215.257 | 40.18 | reference | — |
| owlrl | 100 | turbo-historical | 35.953 | 35.362–39.708 | 41.12 | different | — |
| rdfs | 1000 | turbo-historical | 232.919 | 229.273–304.145 | 69.55 | different | — |
| rdfs | 1000 | python-reference | 915.672 | 907.332–1025.242 | 47.29 | reference | — |
| rdfs | 1000 | candidate | 94.802 | 93.090–98.809 | 56.01 | standard_rdf_equal | — |
| owlrl | 1000 | python-reference | 1446.274 | 1437.837–1567.958 | 48.78 | reference | — |
| owlrl | 1000 | candidate | 88.636 | 87.626–90.325 | 57.33 | standard_rdf_equal | — |
| owlrl | 1000 | turbo-historical | 322.096 | 320.740–329.098 | 76.04 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.5, rdflib-turbo 0.2.0a15

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
