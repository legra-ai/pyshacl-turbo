# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-20T09:47:41.949271+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `3fef1f743bdd05d59f11a19a3c98ea2d30f82b82`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 8.463 | 7.952–10.803 | 49.50 | report_graph_equal | — |
| rdfs | 100 | python-reference | 71.338 | 58.789–89.005 | 47.53 | reference | — |
| rdfs | 100 | turbo-historical | 25.615 | 22.187–35.281 | 47.56 | different | — |
| owlrl | 100 | candidate | 20.176 | 17.140–24.811 | 50.42 | report_graph_equal | — |
| owlrl | 100 | python-reference | 252.899 | 237.220–266.869 | 47.97 | reference | — |
| owlrl | 100 | turbo-historical | 31.273 | 29.099–40.977 | 50.58 | different | — |
| rdfs | 1000 | turbo-historical | 212.309 | 191.552–261.503 | 103.03 | different | — |
| rdfs | 1000 | python-reference | 886.612 | 775.274–1031.129 | 55.41 | reference | — |
| rdfs | 1000 | candidate | 93.107 | 62.883–171.414 | 61.12 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1278.537 | 1236.779–1565.070 | 56.19 | reference | — |
| owlrl | 1000 | candidate | 118.241 | 105.550–125.708 | 63.30 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 289.671 | 248.686–410.017 | 112.22 | different | — |
| rdfs | 10000 | turbo-historical | 4228.342 | 3178.700–4424.569 | 676.11 | different | — |
| rdfs | 10000 | python-reference | 21319.790 | 19108.278–33743.108 | 131.98 | reference | — |
| rdfs | 10000 | candidate | 964.683 | 834.368–2016.302 | 172.47 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 10389.690 | 9910.143–11574.431 | 141.25 | reference | — |
| owlrl | 10000 | candidate | 1381.737 | 1191.651–2012.858 | 203.00 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 3690.307 | 3378.898–4283.846 | 779.81 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
