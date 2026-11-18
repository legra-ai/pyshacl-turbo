# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-18T13:58:37.471365+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `c5c828aa2d37e30f85d97d54815454e8e0baee66`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 12.057 | 8.600–15.916 | 58.00 | equal | 6.14× | — | — |
| pipeline_rdfs | 100 | python-reference | 74.064 | 67.414–82.306 | 59.38 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.723 | 19.922–36.641 | 54.61 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.583 | 15.807–27.051 | 58.66 | equal | 14.19× | — | — |
| pipeline_owlrl | 100 | python-reference | 235.322 | 225.478–282.668 | 59.66 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 40.312 | 32.531–47.176 | 56.86 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 263.629 | 213.561–361.877 | 109.62 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 821.447 | 730.220–1042.877 | 64.86 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 56.802 | 52.229–65.515 | 63.78 | equal | 14.46× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1290.249 | 1240.465–1666.050 | 66.02 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 105.921 | 98.534–158.435 | 63.08 | equal | 12.18× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 370.297 | 323.924–405.019 | 119.59 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 4054.103 | 2982.423–5151.763 | 674.33 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 27128.573 | 23569.816–33409.301 | 140.61 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 1005.385 | 795.846–1695.643 | 129.00 | equal | 26.98× | — | — |
| pipeline_owlrl | 10000 | python-reference | 13141.633 | 10759.711–17273.641 | 149.59 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1086.700 | 1004.734–1798.532 | 121.61 | equal | 12.09× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 6107.761 | 4832.519–7638.936 | 766.34 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 25.769 | 22.021–29.738 | 47.69 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 6.132 | 5.384–10.487 | 55.80 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.969 | 4.849–5.606 | 55.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 26.596 | 26.046–29.436 | 47.69 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 10.089 | 7.516–17.081 | 56.25 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 54.361 | 49.545–58.234 | 47.75 | reference | — | — | — |
| literal-type | 128 | python-reference | 74.117 | 67.560–78.978 | 47.70 | reference | — | — | — |
| literal-type | 128 | candidate | 8.284 | 8.053–9.084 | 56.27 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 218.942 | 191.034–355.614 | 49.27 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.738 | 17.025–28.190 | 58.83 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 242.797 | 239.522–286.336 | 49.59 | reference | — | — | — |
| literal-type | 512 | candidate | 23.271 | 21.571–33.325 | 59.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 29.540 | 28.628–34.650 | 62.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 391.462 | 357.430–460.890 | 51.59 | reference | — | — | — |
| literal-type | 1000 | candidate | 39.072 | 37.306–43.089 | 62.62 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 478.446 | 457.065–539.149 | 52.11 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
