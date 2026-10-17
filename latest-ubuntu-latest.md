# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-17T19:30:55.603092+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `feb2cb0e970bd09cbb131c6ddf96aabbd3f71f05`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.466 | 9.247–12.840 | 41.52 | report_graph_equal | — |
| rdfs | 100 | turbo-historical | 24.235 | 24.046–26.940 | 39.43 | different | — |
| rdfs | 100 | python-reference | 97.392 | 96.903–99.649 | 39.73 | reference | — |
| rdfs | 100 | latest-published | 20.614 | 20.176–23.719 | 39.95 | different | — |
| owlrl | 100 | candidate | 16.552 | 16.246–16.783 | 42.15 | report_graph_equal | — |
| owlrl | 100 | python-reference | 229.326 | 226.834–241.594 | 40.12 | reference | — |
| owlrl | 100 | latest-published | 33.237 | 32.820–36.058 | 41.27 | different | — |
| owlrl | 100 | turbo-historical | 37.586 | 37.308–41.599 | 40.90 | different | — |
| rdfs | 1000 | python-reference | 1013.424 | 1009.420–1109.614 | 47.37 | reference | — |
| rdfs | 1000 | turbo-historical | 244.068 | 234.812–321.294 | 69.07 | different | — |
| rdfs | 1000 | latest-published | 207.624 | 202.452–259.291 | 69.89 | different | — |
| rdfs | 1000 | candidate | 80.309 | 78.363–189.645 | 49.45 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1605.308 | 1569.401–1675.594 | 48.69 | reference | — |
| owlrl | 1000 | latest-published | 291.480 | 289.649–333.928 | 76.56 | different | — |
| owlrl | 1000 | candidate | 123.181 | 121.671–125.845 | 50.84 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 333.427 | 327.943–336.838 | 75.80 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.3.0, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
