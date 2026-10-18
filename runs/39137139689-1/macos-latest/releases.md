# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-18T14:45:52.627222+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `0bc0212b391c338b30d5f7f47e89fe74caea9203`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.756 | 6.843–9.703 | 49.44 | report_graph_equal | — |
| rdfs | 100 | python-reference | 54.119 | 46.916–69.952 | 47.55 | reference | — |
| rdfs | 100 | turbo-historical | 15.182 | 13.330–18.333 | 47.66 | different | — |
| owlrl | 100 | candidate | 11.619 | 11.466–12.214 | 50.16 | report_graph_equal | — |
| owlrl | 100 | python-reference | 120.369 | 117.896–125.969 | 47.70 | reference | — |
| owlrl | 100 | turbo-historical | 22.895 | 22.524–24.607 | 50.55 | different | — |
| rdfs | 1000 | turbo-historical | 134.599 | 131.953–166.310 | 103.94 | different | — |
| rdfs | 1000 | python-reference | 563.481 | 520.156–621.846 | 55.11 | reference | — |
| rdfs | 1000 | candidate | 59.678 | 53.673–110.110 | 61.02 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 939.149 | 836.074–1085.394 | 56.14 | reference | — |
| owlrl | 1000 | candidate | 80.785 | 73.079–84.141 | 63.20 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 169.383 | 167.977–181.541 | 113.81 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
