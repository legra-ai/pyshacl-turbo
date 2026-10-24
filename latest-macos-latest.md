# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-24T15:12:04.034414+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `454eb25f32b3e1a7474da36d551279bd8f71fd28`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 14.560 | 11.020–17.286 | 49.09 | standard_rdf_equal | — |
| rdfs | 100 | python-reference | 74.737 | 64.658–82.391 | 47.67 | reference | — |
| rdfs | 100 | turbo-historical | 17.328 | 16.810–18.853 | 47.64 | different | — |
| owlrl | 100 | candidate | 12.609 | 11.853–17.771 | 49.48 | standard_rdf_equal | — |
| owlrl | 100 | python-reference | 206.456 | 165.799–246.721 | 48.03 | reference | — |
| owlrl | 100 | turbo-historical | 31.164 | 28.084–41.943 | 50.55 | different | — |
| rdfs | 1000 | turbo-historical | 202.753 | 194.744–331.468 | 102.66 | different | — |
| rdfs | 1000 | python-reference | 821.557 | 677.434–974.275 | 55.27 | reference | — |
| rdfs | 1000 | candidate | 82.850 | 80.353–110.109 | 53.77 | standard_rdf_equal | — |
| owlrl | 1000 | python-reference | 1171.918 | 997.873–1264.874 | 56.16 | reference | — |
| owlrl | 1000 | candidate | 74.015 | 73.563–79.877 | 54.16 | standard_rdf_equal | — |
| owlrl | 1000 | turbo-historical | 245.933 | 227.048–310.415 | 114.55 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.6.5, rdflib-turbo 0.2.0a15

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
