# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T14:56:19.678619+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `36b887b30bef8498dc6ec570eb87ad4f133871bc`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.692 | 9.532–13.375 | 57.31 | report_graph_equal | — |
| rdfs | 100 | python-reference | 99.239 | 98.513–103.706 | 39.76 | reference | — |
| rdfs | 100 | turbo-historical | 26.478 | 25.619–32.872 | 41.89 | different | — |
| owlrl | 100 | candidate | 15.052 | 14.834–15.133 | 57.68 | report_graph_equal | — |
| owlrl | 100 | python-reference | 232.227 | 228.068–234.565 | 40.00 | reference | — |
| owlrl | 100 | turbo-historical | 39.615 | 38.630–43.935 | 43.21 | different | — |
| rdfs | 1000 | turbo-historical | 248.635 | 237.232–326.862 | 70.75 | different | — |
| rdfs | 1000 | python-reference | 1029.020 | 1022.435–1143.011 | 47.12 | reference | — |
| rdfs | 1000 | candidate | 83.788 | 82.334–182.056 | 61.04 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1604.185 | 1579.673–1766.929 | 48.70 | reference | — |
| owlrl | 1000 | candidate | 111.567 | 110.700–113.246 | 61.64 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 341.263 | 335.528–343.053 | 77.28 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.5.0, rdflib-turbo 0.2.0a5

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
