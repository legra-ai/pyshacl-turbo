# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-24T13:28:43.095797+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `8042927fcdaddd82c166cff2e8c103c944256135`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 15.510 | 11.252–18.225 | 48.89 | standard_rdf_equal | — |
| rdfs | 100 | python-reference | 70.721 | 59.897–80.096 | 47.55 | reference | — |
| rdfs | 100 | turbo-historical | 21.111 | 19.196–30.079 | 47.67 | different | — |
| owlrl | 100 | candidate | 15.944 | 14.075–24.638 | 49.42 | standard_rdf_equal | — |
| owlrl | 100 | python-reference | 144.333 | 141.813–169.102 | 47.86 | reference | — |
| owlrl | 100 | turbo-historical | 43.829 | 38.090–46.963 | 50.53 | different | — |
| rdfs | 1000 | turbo-historical | 183.621 | 162.270–244.108 | 103.94 | different | — |
| rdfs | 1000 | python-reference | 751.424 | 670.394–1104.881 | 55.28 | reference | — |
| rdfs | 1000 | candidate | 88.745 | 85.604–93.648 | 53.56 | standard_rdf_equal | — |
| owlrl | 1000 | python-reference | 1264.599 | 1156.366–1599.148 | 56.20 | reference | — |
| owlrl | 1000 | candidate | 75.088 | 71.834–76.413 | 54.09 | standard_rdf_equal | — |
| owlrl | 1000 | turbo-historical | 254.148 | 220.205–283.368 | 113.73 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.4, rdflib-turbo 0.2.0a15

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
