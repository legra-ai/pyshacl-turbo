# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T15:35:36.964772+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `36b887b30bef8498dc6ec570eb87ad4f133871bc`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.403 | 6.621–9.742 | 48.12 | report_graph_equal | — |
| rdfs | 100 | python-reference | 60.122 | 53.694–76.364 | 47.50 | reference | — |
| rdfs | 100 | turbo-historical | 15.122 | 14.177–19.199 | 47.62 | different | — |
| owlrl | 100 | candidate | 10.782 | 10.355–11.124 | 48.62 | report_graph_equal | — |
| owlrl | 100 | python-reference | 135.988 | 134.272–173.302 | 47.72 | reference | — |
| owlrl | 100 | turbo-historical | 24.908 | 24.345–26.697 | 50.28 | different | — |
| rdfs | 1000 | turbo-historical | 166.435 | 147.730–267.586 | 103.45 | different | — |
| rdfs | 1000 | python-reference | 696.730 | 628.013–745.935 | 55.19 | reference | — |
| rdfs | 1000 | candidate | 63.539 | 56.940–112.299 | 53.30 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1102.320 | 976.010–1495.933 | 56.06 | reference | — |
| owlrl | 1000 | candidate | 71.175 | 70.205–72.908 | 54.23 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 187.823 | 185.218–197.782 | 112.81 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.5.0, rdflib-turbo 0.2.0a5

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
