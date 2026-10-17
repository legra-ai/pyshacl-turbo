# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-17T17:40:32.930936+00:00; platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39.
Harness revision: `6d70c357ac40829c5a14bb6c8f68a91c52d68ac8`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.424 | 7.268–11.166 | 42.23 | report_graph_equal | — |
| rdfs | 100 | turbo-historical | 16.733 | 16.370–21.435 | 39.29 | different | — |
| rdfs | 100 | python-reference | 67.985 | 65.206–68.842 | 39.48 | reference | — |
| rdfs | 100 | latest-published | 14.914 | 14.414–18.338 | 39.65 | different | — |
| owlrl | 100 | candidate | 13.692 | 13.505–14.034 | 42.75 | report_graph_equal | — |
| owlrl | 100 | python-reference | 152.861 | 151.125–156.379 | 39.94 | reference | — |
| owlrl | 100 | latest-published | 23.635 | 23.176–29.149 | 40.95 | different | — |
| owlrl | 100 | turbo-historical | 26.756 | 26.457–29.588 | 40.69 | different | — |
| rdfs | 1000 | python-reference | 668.171 | 657.296–756.589 | 47.23 | reference | — |
| rdfs | 1000 | turbo-historical | 171.095 | 168.056–278.101 | 69.16 | different | — |
| rdfs | 1000 | latest-published | 148.265 | 144.684–243.591 | 69.23 | different | — |
| rdfs | 1000 | candidate | 73.555 | 70.587–77.701 | 53.67 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1055.190 | 1028.185–1072.359 | 48.52 | reference | — |
| owlrl | 1000 | latest-published | 217.600 | 210.735–303.521 | 75.86 | different | — |
| owlrl | 1000 | candidate | 122.712 | 120.065–125.867 | 62.68 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 241.942 | 234.799–244.284 | 75.75 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.10, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.0, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
