# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-22T23:19:19.675680+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `b8dc84f8238dc097be5aee2982256072b2ac9b5a`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 10.541 | 7.977–14.497 | 54.50 | report_graph_equal | — |
| rdfs | 100 | python-reference | 77.441 | 66.060–86.665 | 47.47 | reference | — |
| rdfs | 100 | turbo-historical | 26.475 | 20.068–29.056 | 47.61 | different | — |
| owlrl | 100 | candidate | 14.573 | 12.869–16.885 | 54.80 | report_graph_equal | — |
| owlrl | 100 | python-reference | 223.634 | 209.854–272.233 | 47.84 | reference | — |
| owlrl | 100 | turbo-historical | 30.432 | 28.368–33.669 | 50.48 | different | — |
| rdfs | 1000 | turbo-historical | 223.951 | 176.661–303.678 | 104.36 | different | — |
| rdfs | 1000 | python-reference | 800.720 | 733.465–1273.368 | 55.23 | reference | — |
| rdfs | 1000 | candidate | 66.062 | 58.920–123.917 | 59.02 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1271.988 | 1191.464–1406.037 | 56.06 | reference | — |
| owlrl | 1000 | candidate | 90.400 | 81.922–104.592 | 59.31 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 307.673 | 276.957–375.450 | 112.14 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.2, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
