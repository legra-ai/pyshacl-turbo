# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-19T10:16:08.732155+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `0bc0212b391c338b30d5f7f47e89fe74caea9203`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 8.726 | 8.202–22.858 | 49.45 | report_graph_equal | — |
| rdfs | 100 | python-reference | 74.247 | 61.221–86.377 | 47.69 | reference | — |
| rdfs | 100 | turbo-historical | 18.997 | 17.238–25.352 | 47.66 | different | — |
| owlrl | 100 | candidate | 15.234 | 14.945–25.096 | 50.45 | report_graph_equal | — |
| owlrl | 100 | python-reference | 217.888 | 182.019–273.574 | 48.05 | reference | — |
| owlrl | 100 | turbo-historical | 41.908 | 32.272–69.276 | 50.58 | different | — |
| rdfs | 1000 | turbo-historical | 283.324 | 259.167–439.957 | 103.61 | different | — |
| rdfs | 1000 | python-reference | 841.741 | 736.012–1031.831 | 55.44 | reference | — |
| rdfs | 1000 | candidate | 73.852 | 67.737–221.287 | 61.34 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1280.992 | 1157.518–1605.649 | 56.27 | reference | — |
| owlrl | 1000 | candidate | 117.866 | 104.011–137.152 | 63.34 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 262.898 | 239.922–338.411 | 111.16 | different | — |
| rdfs | 10000 | turbo-historical | 3726.027 | 2874.612–4263.201 | 671.00 | different | — |
| rdfs | 10000 | python-reference | 19949.660 | 17951.400–25180.018 | 131.94 | reference | — |
| rdfs | 10000 | candidate | 865.235 | 727.323–1331.952 | 172.59 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 10060.322 | 9482.998–11457.511 | 141.20 | reference | — |
| owlrl | 10000 | candidate | 1064.527 | 989.000–1400.752 | 201.83 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 4335.113 | 3433.484–4807.797 | 747.75 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
