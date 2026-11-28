# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T13:25:46.708901+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `5be2fd5b65a8200bb299b744f781034fa902baff`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 13.114 | 7.470–15.370 | 58.00 | equal | 4.99× | — | — |
| pipeline_rdfs | 100 | python-reference | 65.411 | 63.141–71.918 | 59.25 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.363 | 19.564–23.552 | 54.72 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.399 | 16.845–27.693 | 58.61 | equal | 7.87× | — | — |
| pipeline_owlrl | 100 | python-reference | 160.618 | 142.977–198.777 | 59.55 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.132 | 29.888–39.845 | 56.61 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 214.427 | 197.666–292.302 | 109.69 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 705.370 | 631.473–888.563 | 64.83 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 60.935 | 50.800–68.422 | 63.86 | equal | 11.58× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1082.532 | 1010.634–1259.644 | 65.88 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 90.741 | 84.744–113.968 | 63.11 | equal | 11.93× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 268.036 | 243.800–308.843 | 119.59 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 20.318 | 19.981–22.453 | 47.53 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.105 | 3.889–4.691 | 55.78 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 23.255 | 23.016–25.005 | 47.56 | reference | — | — | — |
| literal-type | 32 | candidate | 4.805 | 4.585–5.144 | 55.86 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 50.148 | 48.876–64.445 | 47.55 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.478 | 6.360–6.540 | 56.14 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.759 | 7.569–8.044 | 56.28 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 63.648 | 61.584–75.441 | 47.53 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 15.647 | 14.741–18.324 | 58.73 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 170.535 | 168.719–244.994 | 49.09 | reference | — | — | — |
| literal-type | 512 | python-reference | 229.546 | 208.340–279.477 | 49.59 | reference | — | — | — |
| literal-type | 512 | candidate | 20.454 | 19.367–23.287 | 59.00 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 337.271 | 332.544–388.685 | 51.39 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 30.693 | 27.601–34.691 | 61.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 423.022 | 414.421–475.221 | 51.92 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.157 | 36.920–41.533 | 62.45 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 32 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-type | 32 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-reflexivity | 128 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-type | 128 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-reflexivity | 512 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-type | 512 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-reflexivity | 1000 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |
| literal-type | 1000 | turbo-historical | — | — | — | not measured: Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed | — | not measured | — |

## Exact product versions

- python-reference: owlrl 7.6.2, pyshacl 0.40.1, rdflib 7.6.0
- turbo-historical: owlrl-turbo 0.1.0a2, pyshacl-turbo 0.2.4, rdflib-turbo 0.1.0a2
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.11, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
