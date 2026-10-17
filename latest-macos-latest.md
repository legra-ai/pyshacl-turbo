# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-17T17:33:18.360787+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `6d70c357ac40829c5a14bb6c8f68a91c52d68ac8`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 14.556 | 9.313–22.473 | 46.27 | report_graph_equal | — |
| rdfs | 100 | turbo-historical | 28.021 | 22.173–60.308 | 47.36 | different | — |
| rdfs | 100 | python-reference | 90.743 | 68.415–116.942 | 47.20 | reference | — |
| rdfs | 100 | latest-published | 22.188 | 15.360–23.713 | 47.52 | different | — |
| owlrl | 100 | candidate | 22.774 | 21.174–27.935 | 47.59 | report_graph_equal | — |
| owlrl | 100 | python-reference | 223.401 | 193.506–254.656 | 47.61 | reference | — |
| owlrl | 100 | latest-published | 34.200 | 24.701–42.910 | 50.22 | different | — |
| owlrl | 100 | turbo-historical | 44.489 | 36.755–65.701 | 50.41 | different | — |
| rdfs | 1000 | python-reference | 1051.585 | 854.733–1130.652 | 54.92 | reference | — |
| rdfs | 1000 | turbo-historical | 259.151 | 222.197–433.572 | 102.42 | different | — |
| rdfs | 1000 | latest-published | 250.562 | 189.809–408.755 | 102.34 | different | — |
| rdfs | 1000 | candidate | 104.136 | 92.736–129.296 | 64.50 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1554.254 | 1404.290–1878.829 | 55.83 | reference | — |
| owlrl | 1000 | latest-published | 379.108 | 304.785–942.480 | 112.08 | different | — |
| owlrl | 1000 | candidate | 170.933 | 156.694–219.750 | 75.28 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 401.783 | 275.587–455.243 | 113.59 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.10, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
