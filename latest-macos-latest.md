# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T09:48:30.435466+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `3fef1f743bdd05d59f11a19a3c98ea2d30f82b82`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 11.992 | 9.612–16.927 | 49.62 | report_graph_equal | — |
| rdfs | 100 | python-reference | 63.891 | 56.573–75.963 | 47.56 | reference | — |
| rdfs | 100 | turbo-historical | 20.874 | 18.740–27.456 | 47.66 | different | — |
| owlrl | 100 | candidate | 14.078 | 13.637–21.966 | 50.52 | report_graph_equal | — |
| owlrl | 100 | python-reference | 163.451 | 149.331–195.698 | 48.02 | reference | — |
| owlrl | 100 | turbo-historical | 29.752 | 27.373–33.877 | 50.52 | different | — |
| rdfs | 1000 | turbo-historical | 191.087 | 181.495–279.098 | 103.95 | different | — |
| rdfs | 1000 | python-reference | 710.011 | 688.800–826.144 | 55.36 | reference | — |
| rdfs | 1000 | candidate | 64.439 | 59.264–192.075 | 61.28 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1321.514 | 1198.305–1797.699 | 56.20 | reference | — |
| owlrl | 1000 | candidate | 151.776 | 132.116–205.246 | 63.41 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 382.096 | 325.343–420.844 | 113.14 | different | — |
| rdfs | 10000 | turbo-historical | 4163.446 | 3815.186–4386.142 | 667.17 | different | — |
| rdfs | 10000 | python-reference | 19516.840 | 16140.461–33204.357 | 132.00 | reference | — |
| rdfs | 10000 | candidate | 726.533 | 690.392–1510.516 | 172.77 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 9717.223 | 9647.751–10133.426 | 141.27 | reference | — |
| owlrl | 10000 | candidate | 1160.395 | 1111.751–1892.544 | 201.16 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 4806.734 | 3497.358–6462.333 | 772.70 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.4.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
