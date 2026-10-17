# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-17T19:22:55.752477+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `feb2cb0e970bd09cbb131c6ddf96aabbd3f71f05`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.668 | 9.542–12.937 | 41.54 | report_graph_equal | — |
| rdfs | 100 | turbo-historical | 24.120 | 23.922–27.221 | 39.48 | different | — |
| rdfs | 100 | python-reference | 97.255 | 96.814–102.186 | 39.65 | reference | — |
| rdfs | 100 | latest-published | 20.240 | 19.631–23.383 | 39.86 | different | — |
| owlrl | 100 | candidate | 16.387 | 16.330–16.495 | 42.25 | report_graph_equal | — |
| owlrl | 100 | python-reference | 227.216 | 223.549–246.234 | 40.10 | reference | — |
| owlrl | 100 | latest-published | 32.698 | 32.407–35.666 | 41.27 | different | — |
| owlrl | 100 | turbo-historical | 38.174 | 37.267–40.888 | 40.88 | different | — |
| rdfs | 1000 | python-reference | 998.872 | 993.463–1072.735 | 47.38 | reference | — |
| rdfs | 1000 | turbo-historical | 234.034 | 232.475–289.160 | 69.16 | different | — |
| rdfs | 1000 | latest-published | 196.151 | 193.696–245.783 | 69.90 | different | — |
| rdfs | 1000 | candidate | 78.450 | 77.036–160.479 | 49.35 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1542.554 | 1509.620–1619.861 | 48.72 | reference | — |
| owlrl | 1000 | latest-published | 286.058 | 278.726–317.672 | 76.48 | different | — |
| owlrl | 1000 | candidate | 122.542 | 120.411–124.475 | 51.38 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 320.800 | 313.168–322.168 | 75.84 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.3.0, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
