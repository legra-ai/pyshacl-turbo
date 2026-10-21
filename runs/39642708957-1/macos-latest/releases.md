# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T20:16:42.605239+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `f3344d4202c1c36c62646beb75bfae20fe3ebf95`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 9.688 | 7.286–12.850 | 48.12 | report_graph_equal | — |
| rdfs | 100 | python-reference | 96.960 | 63.973–108.133 | 47.59 | reference | — |
| rdfs | 100 | turbo-historical | 18.554 | 17.564–23.701 | 47.45 | different | — |
| owlrl | 100 | candidate | 12.002 | 10.962–14.381 | 48.69 | report_graph_equal | — |
| owlrl | 100 | python-reference | 171.257 | 165.537–190.194 | 47.81 | reference | — |
| owlrl | 100 | turbo-historical | 37.501 | 33.094–50.291 | 50.36 | different | — |
| rdfs | 1000 | turbo-historical | 213.176 | 186.908–253.759 | 103.16 | different | — |
| rdfs | 1000 | python-reference | 781.612 | 667.258–980.131 | 55.16 | reference | — |
| rdfs | 1000 | candidate | 56.487 | 53.557–73.563 | 52.56 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1069.021 | 1039.649–1122.286 | 56.09 | reference | — |
| owlrl | 1000 | candidate | 78.721 | 69.033–93.889 | 53.53 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 278.606 | 223.364–370.457 | 112.92 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.5.1, rdflib-turbo 0.2.0a5

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
