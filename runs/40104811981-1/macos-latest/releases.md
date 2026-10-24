# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-24T15:28:50.845023+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `14a6f3b3f518b4fe25d6463246d38042ab143e14`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 13.968 | 10.526–22.091 | 49.05 | standard_rdf_equal | — |
| rdfs | 100 | python-reference | 61.379 | 55.210–73.009 | 47.69 | reference | — |
| rdfs | 100 | turbo-historical | 18.026 | 16.945–20.220 | 47.94 | different | — |
| owlrl | 100 | candidate | 10.628 | 10.447–14.535 | 49.48 | standard_rdf_equal | — |
| owlrl | 100 | python-reference | 135.035 | 132.273–171.175 | 48.03 | reference | — |
| owlrl | 100 | turbo-historical | 24.292 | 23.854–26.450 | 50.52 | different | — |
| rdfs | 1000 | turbo-historical | 151.506 | 143.282–182.359 | 103.88 | different | — |
| rdfs | 1000 | python-reference | 581.124 | 572.387–661.623 | 55.36 | reference | — |
| rdfs | 1000 | candidate | 76.314 | 75.820–77.880 | 53.64 | standard_rdf_equal | — |
| owlrl | 1000 | python-reference | 950.503 | 916.365–1044.214 | 56.62 | reference | — |
| owlrl | 1000 | candidate | 67.455 | 66.652–69.636 | 54.25 | standard_rdf_equal | — |
| owlrl | 1000 | turbo-historical | 202.369 | 196.849–234.598 | 111.00 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.5, rdflib-turbo 0.2.0a15

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
