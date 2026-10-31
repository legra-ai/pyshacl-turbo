# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T07:16:58.947495+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `5387c5dc1a4e5ee5a2e5c45778a19e4ffa04b83d`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 14.514 | 14.242–15.922 | 64.47 | equal | 9.13× | — | — |
| pipeline_rdfs | 100 | python-reference | 132.542 | 131.356–135.389 | 47.41 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 34.912 | 34.520–40.691 | 44.41 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 24.411 | 23.623–28.219 | 65.60 | equal | 12.81× | — | — |
| pipeline_owlrl | 100 | python-reference | 312.779 | 310.874–317.657 | 47.68 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 51.946 | 50.733–55.946 | 45.36 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 342.261 | 336.933–462.492 | 73.85 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1309.825 | 1299.021–1393.264 | 52.79 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 108.479 | 107.558–116.033 | 70.15 | equal | 12.07× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2190.604 | 2164.761–2296.312 | 53.85 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 151.323 | 147.234–224.506 | 69.45 | equal | 14.48× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 466.847 | 451.243–571.457 | 80.33 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 50.300 | 48.988–56.781 | 42.92 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.672 | 5.572–5.805 | 63.44 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 54.617 | 54.344–55.541 | 76.67 | reference | — | — | — |
| literal-type | 32 | candidate | 6.282 | 6.199–6.334 | 86.17 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 116.435 | 115.792–116.833 | 110.92 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.443 | 9.259–10.167 | 110.92 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.504 | 11.349–11.701 | 219.01 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 146.948 | 145.162–148.393 | 219.01 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 24.905 | 24.330–25.251 | 330.24 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 392.641 | 390.835–439.900 | 330.24 | reference | — | — | — |
| literal-type | 512 | python-reference | 507.575 | 505.883–559.071 | 646.91 | reference | — | — | — |
| literal-type | 512 | candidate | 33.608 | 33.525–34.122 | 646.91 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 737.352 | 728.325–834.581 | 1055.19 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 44.933 | 44.452–45.378 | 1055.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 974.090 | 963.784–982.723 | 1650.23 | reference | — | — | — |
| literal-type | 1000 | candidate | 60.980 | 60.363–62.960 | 1650.23 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.0, rdflib-turbo 0.2.0a20

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
