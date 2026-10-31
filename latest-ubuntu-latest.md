# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T23:21:58.161630+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `a568c877783ff1b56f97275152191c5d38417149`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 14.022 | 13.555–14.420 | 64.43 | equal | 9.26× | — | — |
| pipeline_rdfs | 100 | python-reference | 129.775 | 128.742–130.154 | 47.27 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 33.550 | 33.017–39.523 | 44.18 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.135 | 22.704–23.969 | 65.52 | equal | 13.56× | — | — |
| pipeline_owlrl | 100 | python-reference | 313.806 | 311.903–319.166 | 47.64 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 50.236 | 49.000–55.387 | 45.41 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 332.991 | 322.929–443.754 | 73.80 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1304.904 | 1288.836–1377.722 | 52.70 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 103.521 | 101.869–104.875 | 70.12 | equal | 12.61× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2187.030 | 2175.931–2291.054 | 53.87 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 139.788 | 138.298–250.830 | 69.39 | equal | 15.65× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 445.117 | 427.017–542.773 | 80.30 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 47.630 | 46.933–49.205 | 42.92 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.473 | 5.341–5.681 | 63.41 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 54.465 | 54.076–54.899 | 76.67 | reference | — | — | — |
| literal-type | 32 | candidate | 6.024 | 5.901–6.136 | 86.17 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 115.372 | 114.902–116.294 | 110.79 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.251 | 9.065–9.563 | 110.79 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.364 | 11.271–11.861 | 219.07 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 143.590 | 143.020–159.581 | 219.07 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 24.120 | 23.846–24.390 | 330.48 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 386.150 | 383.409–420.524 | 330.48 | reference | — | — | — |
| literal-type | 512 | python-reference | 502.027 | 499.200–535.434 | 646.94 | reference | — | — | — |
| literal-type | 512 | candidate | 32.813 | 32.254–33.350 | 646.94 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 735.702 | 726.564–815.512 | 1055.23 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 43.663 | 42.887–44.594 | 1055.23 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 961.782 | 954.778–972.729 | 1650.16 | reference | — | — | — |
| literal-type | 1000 | candidate | 59.688 | 59.097–60.873 | 1650.16 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.3, rdflib-turbo 0.2.0a24

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
