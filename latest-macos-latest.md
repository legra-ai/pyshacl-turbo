# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-16T14:57:52.497325+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `8dbe8d3628800f77a0bee164caaaebff43207eaf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.397 | 7.009–10.645 | 58.19 | equal | 9.93× | — | — |
| pipeline_rdfs | 100 | python-reference | 73.432 | 63.440–115.894 | 59.33 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.137 | 18.883–21.698 | 54.72 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 14.922 | 14.726–15.584 | 58.66 | equal | 9.67× | — | — |
| pipeline_owlrl | 100 | python-reference | 144.334 | 141.181–189.277 | 59.72 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 30.209 | 28.784–32.110 | 56.59 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 212.077 | 177.583–296.532 | 110.11 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 623.884 | 609.753–731.773 | 64.83 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 46.757 | 42.976–49.638 | 63.83 | equal | 13.34× | — | — |
| pipeline_owlrl | 1000 | python-reference | 993.691 | 946.649–1155.792 | 65.86 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 89.663 | 87.970–93.363 | 63.17 | equal | 11.08× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 265.384 | 258.637–306.518 | 120.02 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 22.498 | 21.835–30.655 | 47.66 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.309 | 4.151–5.062 | 55.91 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 25.231 | 24.122–29.035 | 47.67 | reference | — | — | — |
| literal-type | 32 | candidate | 4.677 | 4.649–4.946 | 55.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 59.932 | 53.235–63.468 | 47.69 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.980 | 6.690–7.789 | 56.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.686 | 8.290–12.763 | 56.16 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 69.114 | 66.945–120.549 | 47.59 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.611 | 15.998–17.879 | 58.72 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 203.093 | 178.643–216.534 | 49.31 | reference | — | — | — |
| literal-type | 512 | python-reference | 248.114 | 234.723–305.289 | 49.53 | reference | — | — | — |
| literal-type | 512 | candidate | 25.301 | 23.425–26.973 | 59.02 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 341.259 | 320.303–387.580 | 51.50 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 27.556 | 26.207–30.522 | 62.03 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 522.019 | 441.437–684.876 | 52.09 | reference | — | — | — |
| literal-type | 1000 | candidate | 56.051 | 48.641–81.385 | 62.55 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.2, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
