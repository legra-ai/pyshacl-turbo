# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-19T13:33:37.238961+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.693 | 6.726–8.435 | 58.05 | equal | 8.71× | — | — |
| pipeline_rdfs | 100 | python-reference | 66.965 | 60.359–92.340 | 59.39 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 23.395 | 19.379–26.183 | 54.50 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.194 | 16.300–18.177 | 58.56 | equal | 11.15× | — | — |
| pipeline_owlrl | 100 | python-reference | 191.791 | 164.151–239.007 | 59.73 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.257 | 32.723–49.123 | 56.67 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 201.255 | 191.804–302.310 | 106.95 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 762.079 | 677.819–1086.618 | 64.92 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 55.602 | 47.554–80.303 | 63.77 | equal | 13.71× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1180.613 | 1055.679–1279.973 | 66.09 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 95.881 | 92.253–104.800 | 63.16 | equal | 12.31× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 349.880 | 283.229–426.648 | 116.84 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 21.968 | 21.619–24.734 | 47.67 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.309 | 4.152–9.852 | 55.92 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 25.460 | 23.708–27.443 | 47.61 | reference | — | — | — |
| literal-type | 32 | candidate | 5.060 | 4.510–5.795 | 55.89 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 69.576 | 60.741–73.537 | 47.75 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.061 | 6.922–12.755 | 56.16 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.412 | 7.360–10.972 | 56.25 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 61.118 | 58.355–96.667 | 47.75 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 20.023 | 17.317–22.355 | 58.81 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 224.310 | 201.532–285.424 | 49.27 | reference | — | — | — |
| literal-type | 512 | python-reference | 243.489 | 227.042–323.494 | 49.73 | reference | — | — | — |
| literal-type | 512 | candidate | 27.200 | 25.082–34.645 | 59.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 373.716 | 344.124–428.940 | 51.53 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 30.544 | 29.462–40.692 | 62.14 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 470.756 | 426.969–539.388 | 52.16 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.254 | 36.843–66.110 | 62.61 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
