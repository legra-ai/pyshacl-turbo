# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T22:05:08.143559+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `2329aa7f82359fda530a9377aa555f84ad76f6de`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.954 | 7.739–15.260 | 55.66 | report_graph_equal | — |
| rdfs | 100 | python-reference | 109.777 | 63.179–145.808 | 47.48 | reference | — |
| rdfs | 100 | turbo-historical | 26.724 | 19.310–34.149 | 47.55 | different | — |
| owlrl | 100 | candidate | 16.151 | 11.484–17.997 | 55.95 | report_graph_equal | — |
| owlrl | 100 | python-reference | 179.418 | 161.405–208.788 | 47.91 | reference | — |
| owlrl | 100 | turbo-historical | 27.787 | 23.662–31.864 | 50.23 | different | — |
| rdfs | 1000 | turbo-historical | 196.166 | 159.038–221.426 | 100.17 | different | — |
| rdfs | 1000 | python-reference | 935.153 | 679.607–1243.159 | 55.34 | reference | — |
| rdfs | 1000 | candidate | 61.599 | 58.730–106.845 | 60.09 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1249.965 | 1142.873–1445.931 | 56.16 | reference | — |
| owlrl | 1000 | candidate | 77.969 | 71.030–88.274 | 60.36 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 257.966 | 243.913–324.461 | 110.64 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.0, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
