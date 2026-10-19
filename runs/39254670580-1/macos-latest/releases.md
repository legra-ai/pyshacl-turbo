# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-19T13:15:28.191831+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `7f7516b97c3a7fb3ac0cf03bfec7c83ffa8e7539`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 18.448 | 13.409–29.106 | 49.69 | report_graph_equal | — |
| rdfs | 100 | python-reference | 109.870 | 95.425–122.753 | 47.67 | reference | — |
| rdfs | 100 | turbo-historical | 29.471 | 21.314–33.508 | 47.78 | different | — |
| owlrl | 100 | candidate | 23.340 | 15.019–26.275 | 50.47 | report_graph_equal | — |
| owlrl | 100 | python-reference | 242.813 | 222.861–294.165 | 48.02 | reference | — |
| owlrl | 100 | turbo-historical | 41.303 | 39.063–48.312 | 50.73 | different | — |
| rdfs | 1000 | turbo-historical | 283.286 | 254.299–400.628 | 103.77 | different | — |
| rdfs | 1000 | python-reference | 1126.895 | 990.757–1325.989 | 55.45 | reference | — |
| rdfs | 1000 | candidate | 112.360 | 83.742–165.063 | 61.19 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1914.951 | 1720.545–2175.747 | 56.19 | reference | — |
| owlrl | 1000 | candidate | 130.090 | 120.178–149.210 | 63.31 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 385.543 | 310.871–458.104 | 113.84 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
