# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T20:37:06.343921+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `f3344d4202c1c36c62646beb75bfae20fe3ebf95`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 8.868 | 7.117–10.128 | 48.30 | report_graph_equal | — |
| rdfs | 100 | python-reference | 81.500 | 62.259–102.381 | 47.70 | reference | — |
| rdfs | 100 | turbo-historical | 26.599 | 20.099–29.697 | 47.84 | different | — |
| owlrl | 100 | candidate | 12.839 | 11.469–17.966 | 48.86 | report_graph_equal | — |
| owlrl | 100 | python-reference | 227.769 | 186.279–276.157 | 47.98 | reference | — |
| owlrl | 100 | turbo-historical | 34.982 | 28.864–62.243 | 50.66 | different | — |
| rdfs | 1000 | turbo-historical | 221.330 | 212.323–303.522 | 104.03 | different | — |
| rdfs | 1000 | python-reference | 794.241 | 628.778–993.299 | 55.23 | reference | — |
| rdfs | 1000 | candidate | 67.572 | 60.077–104.657 | 52.64 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1652.370 | 1259.544–2274.540 | 56.28 | reference | — |
| owlrl | 1000 | candidate | 76.212 | 74.993–86.628 | 53.66 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 313.493 | 277.538–362.505 | 114.12 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.5.1, rdflib-turbo 0.2.0a5

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
