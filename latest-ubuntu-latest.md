# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-22T09:38:26.635004+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `9fe810ac014092bad5e77e1c6ed0df0d490da4a8`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.463 | 7.387–7.565 | 59.35 | report_graph_equal | — |
| rdfs | 100 | python-reference | 68.996 | 68.474–72.763 | 39.84 | reference | — |
| rdfs | 100 | turbo-historical | 18.938 | 18.634–23.756 | 39.51 | different | — |
| owlrl | 100 | candidate | 10.794 | 10.651–11.067 | 59.83 | report_graph_equal | — |
| owlrl | 100 | python-reference | 164.584 | 162.209–167.191 | 40.09 | reference | — |
| owlrl | 100 | turbo-historical | 30.232 | 29.821–34.113 | 40.80 | different | — |
| rdfs | 1000 | turbo-historical | 197.042 | 187.648–293.866 | 69.08 | different | — |
| rdfs | 1000 | python-reference | 729.416 | 724.356–806.659 | 47.16 | reference | — |
| rdfs | 1000 | candidate | 65.445 | 64.656–130.263 | 62.34 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1162.866 | 1117.552–1309.852 | 48.82 | reference | — |
| owlrl | 1000 | candidate | 80.625 | 79.004–82.005 | 63.16 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 253.912 | 250.280–256.217 | 75.80 | different | — |
| rdfs | 10000 | turbo-historical | 3039.546 | 2875.791–3586.969 | 391.01 | different | — |
| rdfs | 10000 | python-reference | 19374.563 | 18797.500–20235.279 | 117.74 | reference | — |
| rdfs | 10000 | candidate | 758.366 | 724.631–780.593 | 93.94 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 11828.107 | 11678.867–12524.611 | 123.36 | reference | — |
| owlrl | 10000 | candidate | 938.159 | 919.732–1671.672 | 96.41 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 4225.793 | 3950.455–5326.328 | 449.64 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.0, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
