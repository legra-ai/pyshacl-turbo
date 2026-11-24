# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-24T15:20:09.450787+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.067 | 7.208–12.648 | 58.11 | equal | 8.28× | — | — |
| pipeline_rdfs | 100 | python-reference | 66.813 | 62.362–79.919 | 59.45 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 23.617 | 21.608–26.696 | 54.62 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.398 | 15.424–24.819 | 58.72 | equal | 13.56× | — | — |
| pipeline_owlrl | 100 | python-reference | 222.367 | 163.979–268.069 | 59.70 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 35.790 | 33.290–44.516 | 56.69 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 231.283 | 191.105–251.616 | 106.98 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 899.733 | 675.089–1002.036 | 64.95 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 60.843 | 51.856–102.078 | 63.81 | equal | 14.79× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1101.771 | 1035.227–1521.226 | 66.16 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 110.774 | 95.609–148.248 | 63.20 | equal | 9.95× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 393.245 | 309.368–466.391 | 115.62 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 4240.777 | 3395.927–5445.379 | 649.81 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 25308.668 | 20659.542–35643.773 | 140.61 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 601.820 | 514.041–774.286 | 127.91 | equal | 42.05× | — | — |
| pipeline_owlrl | 10000 | python-reference | 13480.168 | 10883.933–14246.795 | 149.75 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1222.074 | 1141.548–1683.070 | 121.45 | equal | 11.03× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5504.196 | 5149.396–5940.028 | 745.06 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 27.417 | 25.119–29.321 | 47.75 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.814 | 4.509–5.455 | 56.02 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.791 | 4.731–5.028 | 55.92 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 25.304 | 24.828–25.948 | 47.78 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.861 | 7.700–8.741 | 56.27 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 67.393 | 63.868–92.767 | 47.78 | reference | — | — | — |
| literal-type | 128 | python-reference | 71.634 | 69.096–87.552 | 47.78 | reference | — | — | — |
| literal-type | 128 | candidate | 9.515 | 8.147–9.684 | 56.31 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 198.684 | 180.670–238.006 | 49.41 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 20.497 | 19.858–25.520 | 58.81 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 245.000 | 233.437–298.871 | 49.64 | reference | — | — | — |
| literal-type | 512 | candidate | 26.619 | 22.808–34.031 | 59.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 35.954 | 34.844–37.566 | 62.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 447.667 | 408.420–576.883 | 51.62 | reference | — | — | — |
| literal-type | 1000 | candidate | 51.618 | 41.242–66.628 | 62.62 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 505.547 | 441.195–520.754 | 52.19 | reference | — | — | — |
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
