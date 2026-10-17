# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-17T19:32:30.066163+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `feb2cb0e970bd09cbb131c6ddf96aabbd3f71f05`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 11.587 | 9.346–14.905 | 45.91 | report_graph_equal | — |
| rdfs | 100 | turbo-historical | 28.191 | 24.968–44.572 | 47.42 | different | — |
| rdfs | 100 | python-reference | 111.375 | 67.550–123.146 | 47.77 | reference | — |
| rdfs | 100 | latest-published | 19.902 | 15.795–29.558 | 47.91 | different | — |
| owlrl | 100 | candidate | 18.356 | 13.737–22.723 | 46.56 | report_graph_equal | — |
| owlrl | 100 | python-reference | 229.012 | 201.641–315.443 | 48.00 | reference | — |
| owlrl | 100 | latest-published | 32.945 | 26.979–45.600 | 50.70 | different | — |
| owlrl | 100 | turbo-historical | 35.620 | 30.931–48.368 | 50.42 | different | — |
| rdfs | 1000 | python-reference | 985.645 | 878.501–1095.565 | 55.39 | reference | — |
| rdfs | 1000 | turbo-historical | 207.440 | 170.435–263.023 | 104.05 | different | — |
| rdfs | 1000 | latest-published | 225.241 | 197.456–297.958 | 103.14 | different | — |
| rdfs | 1000 | candidate | 93.862 | 74.818–213.550 | 57.78 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1390.369 | 1170.876–1611.852 | 56.17 | reference | — |
| owlrl | 1000 | latest-published | 327.347 | 256.683–355.086 | 112.42 | different | — |
| owlrl | 1000 | candidate | 129.606 | 96.028–159.360 | 59.48 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 328.472 | 247.984–401.307 | 113.55 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- latest-published: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.3.0, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.3.1, rdflib-turbo 0.2.0a1

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
