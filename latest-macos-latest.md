# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners.

Measured: 2026-10-21T14:23:18.315880+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `f1a7d3ba9dee70d6ce95b75836dc8f511e03627c`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Pipeline | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python |
|---|---:|---|---:|---:|---:|---|---:|
| rdfs | 100 | candidate | 11.666 | 7.989–13.271 | 47.88 | report_graph_equal | — |
| rdfs | 100 | python-reference | 81.207 | 65.754–96.498 | 47.58 | reference | — |
| rdfs | 100 | turbo-historical | 33.905 | 29.657–47.145 | 47.73 | different | — |
| owlrl | 100 | candidate | 19.601 | 12.275–29.797 | 48.33 | report_graph_equal | — |
| owlrl | 100 | python-reference | 202.176 | 182.887–240.262 | 47.86 | reference | — |
| owlrl | 100 | turbo-historical | 28.945 | 25.924–40.791 | 50.52 | different | — |
| rdfs | 1000 | turbo-historical | 244.288 | 204.715–300.616 | 103.66 | different | — |
| rdfs | 1000 | python-reference | 757.565 | 637.295–1000.233 | 55.30 | reference | — |
| rdfs | 1000 | candidate | 61.725 | 58.874–157.141 | 52.86 | report_graph_equal | — |
| owlrl | 1000 | python-reference | 1211.625 | 1070.295–1716.099 | 56.14 | reference | — |
| owlrl | 1000 | candidate | 97.957 | 82.164–128.021 | 53.89 | report_graph_equal | — |
| owlrl | 1000 | turbo-historical | 231.564 | 212.588–280.866 | 113.11 | different | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.1.0a3, pyshacl-turbo 0.5.0, rdflib-turbo 0.2.0a5

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
