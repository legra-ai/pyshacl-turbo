# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-23T13:19:14.255932+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `f6b6ec015698c324c4a9541463ecb765f2ae0419`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.105 | 9.043–9.179 | 57.73 | report_graph_equal | — |
| rdfs | 100 | python-reference | 96.256 | 95.910–100.167 | 39.62 | reference | — |
| rdfs | 100 | turbo-historical | 24.119 | 23.914–29.096 | 39.43 | different | — |
| owlrl | 100 | candidate | 12.669 | 12.593–12.816 | 58.34 | report_graph_equal | — |
| owlrl | 100 | python-reference | 226.155 | 224.337–229.330 | 40.10 | reference | — |
| owlrl | 100 | turbo-historical | 37.975 | 37.467–41.097 | 40.80 | different | — |
| rdfs | 1000 | turbo-historical | 241.504 | 237.100–303.275 | 69.10 | different | — |
| rdfs | 1000 | python-reference | 1002.653 | 995.312–1089.510 | 47.28 | reference | — |
| rdfs | 1000 | candidate | 77.896 | 77.567–130.855 | 60.77 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1573.069 | 1558.022–1671.351 | 48.68 | reference | — |
| owlrl | 1000 | candidate | 94.706 | 94.473–96.094 | 61.64 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 322.472 | 318.477–327.027 | 75.78 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.3, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
