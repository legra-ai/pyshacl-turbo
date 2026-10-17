# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-17T17:29:33.842501+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `6d70c357ac40829c5a14bb6c8f68a91c52d68ac8`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 6.439 | 6.282–8.550 | 42.23 | report_graph_equal | — |
| rdfs | 100 | turbo-historical | 15.451 | 13.648–26.488 | 39.27 | different | — |
| rdfs | 100 | python-reference | 51.918 | 49.461–71.747 | 39.58 | reference | — |
| rdfs | 100 | latest-published | 11.756 | 11.521–13.651 | 39.50 | different | — |
| owlrl | 100 | candidate | 11.715 | 11.560–11.866 | 42.66 | report_graph_equal | — |
| owlrl | 100 | python-reference | 116.964 | 115.361–128.138 | 39.88 | reference | — |
| owlrl | 100 | latest-published | 19.265 | 18.865–21.745 | 40.93 | different | — |
| owlrl | 100 | turbo-historical | 21.755 | 21.284–23.674 | 40.62 | different | — |
| rdfs | 1000 | python-reference | 498.128 | 486.948–604.401 | 47.16 | reference | — |
| rdfs | 1000 | turbo-historical | 137.601 | 131.711–244.799 | 68.99 | different | — |
| rdfs | 1000 | latest-published | 119.826 | 115.044–231.964 | 69.12 | different | — |
| rdfs | 1000 | candidate | 57.065 | 56.523–58.852 | 53.44 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 809.479 | 793.558–819.218 | 48.46 | reference | — |
| owlrl | 1000 | latest-published | 167.932 | 167.050–267.263 | 75.88 | different | — |
| owlrl | 1000 | candidate | 95.397 | 94.525–96.710 | 63.66 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 196.239 | 192.128–199.494 | 75.69 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.10, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
