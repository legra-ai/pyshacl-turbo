# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-23T11:07:19.314795+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `b8dc84f8238dc097be5aee2982256072b2ac9b5a`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 7.578 | 7.294–13.064 | 54.59 | report_graph_equal | — |
| rdfs | 100 | python-reference | 78.895 | 63.418–121.404 | 47.55 | reference | — |
| rdfs | 100 | turbo-historical | 19.753 | 16.409–25.816 | 47.66 | different | — |
| owlrl | 100 | candidate | 11.897 | 11.314–13.943 | 54.75 | report_graph_equal | — |
| owlrl | 100 | python-reference | 167.573 | 146.243–181.342 | 47.89 | reference | — |
| owlrl | 100 | turbo-historical | 26.530 | 25.532–29.569 | 50.42 | different | — |
| rdfs | 1000 | turbo-historical | 157.782 | 148.776–214.012 | 104.05 | different | — |
| rdfs | 1000 | python-reference | 674.413 | 633.966–949.088 | 55.05 | reference | — |
| rdfs | 1000 | candidate | 73.722 | 60.355–131.540 | 58.97 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1216.728 | 1056.825–1739.590 | 56.05 | reference | — |
| owlrl | 1000 | candidate | 83.819 | 72.384–92.899 | 59.28 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 254.131 | 223.884–310.713 | 114.05 | different | — |
| rdfs | 10000 | turbo-historical | 3367.582 | 3142.355–3434.916 | 676.75 | different | — |
| rdfs | 10000 | python-reference | 29508.865 | 28160.870–30298.404 | 131.94 | reference | — |
| rdfs | 10000 | candidate | 884.731 | 788.680–1145.203 | 104.98 | report_graph_equal | — |
| owlrl | 10000 | python-reference | 12215.159 | 11835.531–13008.975 | 141.08 | reference | — |
| owlrl | 10000 | candidate | 1165.849 | 990.840–1507.528 | 118.50 | report_graph_equal | — |
| owlrl | 10000 | turbo-historical | 4831.908 | 3805.502–5629.504 | 779.53 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.2, rdflib-turbo 0.2.0a7

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
