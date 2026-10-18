# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-18T15:04:54.236291+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `0bc0212b391c338b30d5f7f47e89fe74caea9203`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 6.294 | 5.746–9.327 | 50.86 | report_graph_equal | — |
| rdfs | 100 | python-reference | 51.865 | 50.551–55.623 | 39.80 | reference | — |
| rdfs | 100 | turbo-historical | 16.281 | 15.369–20.810 | 39.42 | different | — |
| owlrl | 100 | candidate | 11.337 | 11.045–11.740 | 51.46 | report_graph_equal | — |
| owlrl | 100 | python-reference | 123.013 | 121.080–125.872 | 40.06 | reference | — |
| owlrl | 100 | turbo-historical | 23.713 | 23.309–26.595 | 40.88 | different | — |
| rdfs | 1000 | turbo-historical | 154.683 | 143.465–227.398 | 69.07 | different | — |
| rdfs | 1000 | python-reference | 546.922 | 534.197–660.825 | 47.23 | reference | — |
| rdfs | 1000 | candidate | 52.805 | 52.035–174.549 | 58.63 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 835.310 | 809.931–964.590 | 48.66 | reference | — |
| owlrl | 1000 | candidate | 78.623 | 76.240–97.798 | 60.31 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 210.074 | 206.919–215.084 | 75.69 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
