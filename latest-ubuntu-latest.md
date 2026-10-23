# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-23T13:53:37.078767+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `f6b6ec015698c324c4a9541463ecb765f2ae0419`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.192 | 9.149–9.273 | 57.73 | report_graph_equal | — |
| rdfs | 100 | python-reference | 97.695 | 96.847–101.447 | 39.72 | reference | — |
| rdfs | 100 | turbo-historical | 24.846 | 24.280–27.472 | 39.44 | different | — |
| owlrl | 100 | candidate | 12.998 | 12.908–13.340 | 58.23 | report_graph_equal | — |
| owlrl | 100 | python-reference | 228.616 | 224.624–233.779 | 40.09 | reference | — |
| owlrl | 100 | turbo-historical | 38.655 | 37.799–41.895 | 40.89 | different | — |
| rdfs | 1000 | turbo-historical | 243.439 | 233.812–297.979 | 69.10 | different | — |
| rdfs | 1000 | python-reference | 1003.699 | 996.370–1096.109 | 47.39 | reference | — |
| rdfs | 1000 | candidate | 77.946 | 77.435–127.769 | 60.83 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1533.708 | 1512.806–1626.938 | 48.68 | reference | — |
| owlrl | 1000 | candidate | 94.992 | 93.940–96.038 | 61.56 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 317.822 | 313.858–322.781 | 75.79 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.3, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
