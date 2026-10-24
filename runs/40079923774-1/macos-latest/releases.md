# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-24T09:16:40.310260+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `f6b6ec015698c324c4a9541463ecb765f2ae0419`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 12.650 | 7.564–22.149 | 54.56 | report_graph_equal | — |
| rdfs | 100 | python-reference | 61.729 | 60.088–70.374 | 47.55 | reference | — |
| rdfs | 100 | turbo-historical | 18.046 | 17.058–26.106 | 47.69 | different | — |
| owlrl | 100 | candidate | 13.437 | 10.821–21.355 | 54.91 | report_graph_equal | — |
| owlrl | 100 | python-reference | 150.537 | 144.666–220.954 | 47.95 | reference | — |
| owlrl | 100 | turbo-historical | 27.706 | 26.032–30.438 | 50.52 | different | — |
| rdfs | 1000 | turbo-historical | 213.732 | 193.199–283.825 | 103.84 | different | — |
| rdfs | 1000 | python-reference | 749.462 | 716.942–815.940 | 55.23 | reference | — |
| rdfs | 1000 | candidate | 91.201 | 68.736–136.876 | 59.08 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1165.212 | 1033.582–1524.314 | 56.11 | reference | — |
| owlrl | 1000 | candidate | 75.826 | 73.191–91.961 | 59.36 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 288.958 | 246.422–343.912 | 113.77 | different | — |
| rdfs | 10000 | turbo-historical | 3640.991 | 3187.942–4223.924 | 672.22 | different | — |
| rdfs | 10000 | python-reference | 20760.482 | 17747.101–27732.881 | 131.91 | reference | — |
| rdfs | 10000 | candidate | 845.391 | 657.528–978.353 | 104.91 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 10850.396 | 9472.474–12492.017 | 141.20 | reference | — |
| owlrl | 10000 | candidate | 847.347 | 720.162–1473.559 | 117.83 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 3012.680 | 2836.417–3333.535 | 752.91 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.3, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
