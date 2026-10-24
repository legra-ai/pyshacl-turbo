# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-24T14:25:19.313493+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `454eb25f32b3e1a7474da36d551279bd8f71fd28`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 17.170 | 16.371–20.637 | 49.08 | standard_rdf_equal | — |
| rdfs | 100 | python-reference | 59.400 | 58.496–67.955 | 47.70 | reference | — |
| rdfs | 100 | turbo-historical | 17.365 | 16.866–20.481 | 47.89 | different | — |
| owlrl | 100 | candidate | 12.810 | 11.626–18.895 | 49.62 | standard_rdf_equal | — |
| owlrl | 100 | python-reference | 171.170 | 160.021–184.603 | 47.94 | reference | — |
| owlrl | 100 | turbo-historical | 35.675 | 27.482–53.912 | 50.52 | different | — |
| rdfs | 1000 | turbo-historical | 282.562 | 184.589–383.697 | 104.12 | different | — |
| rdfs | 1000 | python-reference | 680.365 | 622.331–779.511 | 55.30 | reference | — |
| rdfs | 1000 | candidate | 84.068 | 82.694–121.316 | 53.78 | standard_rdf_equal | — |
| owlrl | 1000 | python-reference | 1184.073 | 1044.148–1384.284 | 56.23 | reference | — |
| owlrl | 1000 | candidate | 76.643 | 72.635–89.153 | 54.23 | standard_rdf_equal | — |
| owlrl | 1000 | turbo-historical | 320.425 | 230.538–369.555 | 114.31 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.5, rdflib-turbo 0.2.0a15

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
