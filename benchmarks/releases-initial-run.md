# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-17T15:33:53.687150+00:00; platform: macOS-27.0.1-arm64-arm-64bit-Mach-O.
Harness revision: `4534553f6c7c1eddf4b16e2a9bee7f9d85c8816c`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.134 | 6.729–8.900 | 46.64 | report_graph_equal | — |
| rdfs | 100 | turbo-historical | 14.938 | 14.520–18.120 | 47.64 | different | — |
| rdfs | 100 | python-reference | 52.973 | 51.431–54.151 | 47.33 | reference | — |
| rdfs | 100 | latest-published | 12.812 | 10.821–14.147 | 47.98 | different | — |
| owlrl | 100 | candidate | 13.331 | 11.675–13.859 | 48.52 | report_graph_equal | — |
| owlrl | 100 | python-reference | 122.800 | 118.136–131.229 | 47.38 | reference | — |
| owlrl | 100 | latest-published | 21.002 | 20.453–23.540 | 50.23 | different | — |
| owlrl | 100 | turbo-historical | 24.118 | 23.250–25.865 | 50.42 | different | — |
| rdfs | 1000 | python-reference | 565.940 | 553.416–608.406 | 54.98 | reference | — |
| rdfs | 1000 | turbo-historical | 137.478 | 130.563–186.320 | 106.08 | different | — |
| rdfs | 1000 | latest-published | 118.820 | 116.794–164.999 | 104.12 | different | — |
| rdfs | 1000 | candidate | 61.924 | 54.518–78.802 | 65.33 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 908.723 | 900.833–917.051 | 56.00 | reference | — |
| owlrl | 1000 | latest-published | 169.035 | 164.789–218.420 | 116.58 | different | — |
| owlrl | 1000 | candidate | 100.883 | 92.934–105.257 | 77.34 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 190.678 | 179.168–195.760 | 113.92 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.10, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.2.10, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.

Raw evidence: [compressed JSON](releases-initial-run.json.gz). This measured the initial shared-runtime candidate identified by its retained source revisions and wheel hashes.
