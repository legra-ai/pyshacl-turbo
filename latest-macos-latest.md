# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-22T10:58:42.325853+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `9fe810ac014092bad5e77e1c6ed0df0d490da4a8`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 5.943 | 5.748–7.081 | 55.61 | report_graph_equal | — |
| rdfs | 100 | python-reference | 57.691 | 52.023–59.856 | 47.53 | reference | — |
| rdfs | 100 | turbo-historical | 13.431 | 13.041–16.369 | 47.33 | different | — |
| owlrl | 100 | candidate | 8.326 | 8.106–8.697 | 55.84 | report_graph_equal | — |
| owlrl | 100 | python-reference | 122.266 | 115.061–134.128 | 47.75 | reference | — |
| owlrl | 100 | turbo-historical | 24.387 | 23.362–26.547 | 50.08 | different | — |
| rdfs | 1000 | turbo-historical | 133.771 | 132.934–169.746 | 99.69 | different | — |
| rdfs | 1000 | python-reference | 560.253 | 526.703–623.215 | 55.11 | reference | — |
| rdfs | 1000 | candidate | 55.429 | 50.237–96.946 | 60.02 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 855.298 | 817.496–955.292 | 56.08 | reference | — |
| owlrl | 1000 | candidate | 66.153 | 64.478–68.021 | 60.39 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 187.684 | 179.766–202.195 | 110.42 | different | — |
| rdfs | 10000 | turbo-historical | 2037.039 | 1942.503–2244.640 | 635.88 | different | — |
| rdfs | 10000 | python-reference | 13244.126 | 13057.601–13544.903 | 131.81 | reference | — |
| rdfs | 10000 | candidate | 540.023 | 514.741–564.066 | 106.25 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 8317.836 | 8133.388–8560.508 | 141.09 | reference | — |
| owlrl | 10000 | candidate | 667.710 | 617.816–1133.899 | 119.66 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 2949.626 | 2760.897–3783.571 | 752.98 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.0, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
