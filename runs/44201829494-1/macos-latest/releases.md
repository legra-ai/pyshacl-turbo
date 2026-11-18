# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-18T00:04:08.749923+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `2a83794827c5f5dc048128ea2d5dbfe51fda5f90`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 6.790 | 5.747–8.531 | 58.05 | equal | 8.45× | — | — |
| pipeline_rdfs | 100 | python-reference | 57.399 | 52.827–60.770 | 59.20 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 19.733 | 18.979–23.382 | 54.48 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 13.855 | 13.659–15.141 | 58.59 | equal | 10.91× | — | — |
| pipeline_owlrl | 100 | python-reference | 151.111 | 134.891–157.896 | 59.55 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 27.521 | 26.165–28.870 | 56.72 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 177.978 | 163.090–225.334 | 109.39 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 584.761 | 562.686–615.370 | 64.72 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 49.832 | 48.706–66.283 | 63.80 | equal | 11.73× | — | — |
| pipeline_owlrl | 1000 | python-reference | 917.149 | 881.489–948.712 | 65.89 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 79.946 | 78.477–80.847 | 63.02 | equal | 11.47× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 282.259 | 222.034–350.658 | 118.17 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 19.557 | 18.869–22.422 | 47.58 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.565 | 3.547–3.704 | 55.78 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 21.819 | 21.586–22.774 | 47.56 | reference | — | — | — |
| literal-type | 32 | candidate | 4.031 | 3.977–4.363 | 55.83 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 48.254 | 47.687–50.927 | 47.53 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.531 | 7.127–14.651 | 56.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.096 | 7.417–9.607 | 56.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 58.799 | 58.047–62.087 | 47.61 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 15.138 | 14.554–17.049 | 58.80 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 185.633 | 172.333–219.297 | 49.20 | reference | — | — | — |
| literal-type | 512 | python-reference | 307.597 | 247.924–380.239 | 49.50 | reference | — | — | — |
| literal-type | 512 | candidate | 24.952 | 21.855–37.824 | 59.03 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 418.286 | 382.044–485.936 | 51.39 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 34.254 | 27.867–40.195 | 61.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 469.282 | 452.250–550.009 | 51.97 | reference | — | — | — |
| literal-type | 1000 | candidate | 40.821 | 38.921–42.448 | 62.53 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.3, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
