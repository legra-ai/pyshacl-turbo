# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T01:42:15.111348+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `1b741cc9a6cf11bbf9728db421f0e3596bbd4c2a`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.341 | 8.933–13.773 | 76.72 | equal | 10.26× | — | — |
| pipeline_rdfs | 100 | python-reference | 95.882 | 95.334–99.731 | 55.68 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 28.394 | 27.813–34.169 | 54.32 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.361 | 19.944–20.778 | 77.38 | equal | 10.97× | — | — |
| pipeline_owlrl | 100 | python-reference | 223.388 | 221.642–226.589 | 56.00 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 41.962 | 41.777–47.067 | 54.31 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 275.256 | 270.373–375.982 | 82.57 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1024.421 | 1004.006–1119.273 | 61.17 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 66.364 | 65.262–69.076 | 80.89 | equal | 15.44× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1561.396 | 1542.376–1673.869 | 62.16 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 127.432 | 125.935–127.818 | 81.25 | equal | 12.25× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 370.996 | 364.236–439.349 | 88.64 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.719 | 32.335–32.950 | 52.46 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.929 | 4.831–5.056 | 74.42 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 38.278 | 37.724–40.563 | 86.34 | reference | — | — | — |
| literal-type | 32 | candidate | 5.538 | 5.381–5.599 | 95.84 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 79.601 | 79.435–80.523 | 120.71 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.275 | 8.125–8.378 | 120.71 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.415 | 10.110–11.406 | 229.07 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 100.793 | 100.536–102.090 | 229.07 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.334 | 20.990–21.652 | 340.27 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 267.972 | 265.774–303.380 | 340.27 | reference | — | — | — |
| literal-type | 512 | python-reference | 352.019 | 349.841–386.753 | 656.43 | reference | — | — | — |
| literal-type | 512 | candidate | 29.066 | 28.662–32.599 | 656.43 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 516.487 | 513.674–608.490 | 1064.71 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 38.015 | 37.215–38.864 | 1064.71 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 677.666 | 673.405–684.656 | 1660.23 | reference | — | — | — |
| literal-type | 1000 | candidate | 52.898 | 52.560–53.773 | 1660.23 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.7, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
