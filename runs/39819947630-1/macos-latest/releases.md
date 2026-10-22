# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-22T17:22:13.066683+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `576afa30e7fa8bc0c446b1e871bc75c0590a2b33`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.060 | 6.568–9.943 | 55.59 | report_graph_equal | — |
| rdfs | 100 | python-reference | 61.873 | 58.783–68.058 | 47.44 | reference | — |
| rdfs | 100 | turbo-historical | 19.213 | 15.971–54.284 | 47.73 | different | — |
| owlrl | 100 | candidate | 10.186 | 9.611–11.978 | 55.91 | report_graph_equal | — |
| owlrl | 100 | python-reference | 160.063 | 139.398–241.545 | 47.86 | reference | — |
| owlrl | 100 | turbo-historical | 24.566 | 23.987–31.309 | 50.58 | different | — |
| rdfs | 1000 | turbo-historical | 177.225 | 159.434–375.385 | 103.64 | different | — |
| rdfs | 1000 | python-reference | 706.933 | 638.780–880.416 | 55.20 | reference | — |
| rdfs | 1000 | candidate | 57.193 | 54.079–96.215 | 59.98 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 987.008 | 942.275–1007.509 | 56.03 | reference | — |
| owlrl | 1000 | candidate | 69.601 | 65.910–73.749 | 60.38 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 213.407 | 196.520–246.391 | 113.97 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.0, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
