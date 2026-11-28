# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T01:46:44.419398+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `1b741cc9a6cf11bbf9728db421f0e3596bbd4c2a`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.461 | 7.907–12.731 | 58.03 | equal | 7.68× | — | — |
| pipeline_rdfs | 100 | python-reference | 72.620 | 68.366–75.615 | 59.27 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.509 | 19.073–29.041 | 54.66 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.987 | 15.551–17.801 | 58.70 | equal | 13.62× | — | — |
| pipeline_owlrl | 100 | python-reference | 217.790 | 187.248–239.306 | 59.58 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 37.898 | 32.253–48.186 | 56.92 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 209.974 | 188.758–291.640 | 110.05 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 784.177 | 724.511–1107.935 | 64.75 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 61.384 | 48.531–94.508 | 63.70 | equal | 12.78× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1632.865 | 1188.078–1949.165 | 65.94 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 96.824 | 90.399–114.459 | 63.09 | equal | 16.86× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 315.519 | 276.396–393.598 | 119.91 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 26.727 | 22.078–33.697 | 47.45 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.466 | 4.235–5.166 | 55.75 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 30.011 | 26.203–40.838 | 47.59 | reference | — | — | — |
| literal-type | 32 | candidate | 6.875 | 5.399–7.683 | 55.78 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 73.281 | 66.511–112.876 | 47.53 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.048 | 6.949–7.457 | 56.00 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.561 | 9.328–9.799 | 56.25 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 82.347 | 80.369–94.843 | 47.53 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 22.766 | 18.523–28.326 | 58.73 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 270.106 | 245.961–318.984 | 49.16 | reference | — | — | — |
| literal-type | 512 | python-reference | 371.339 | 348.587–475.645 | 49.44 | reference | — | — | — |
| literal-type | 512 | candidate | 40.035 | 36.846–46.763 | 58.89 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 654.970 | 543.074–812.436 | 51.36 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 61.662 | 35.992–76.724 | 62.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 631.924 | 528.264–721.659 | 51.92 | reference | — | — | — |
| literal-type | 1000 | candidate | 46.458 | 44.620–66.041 | 62.58 | different | — | logical_inplace_owlrl_different | — |
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
