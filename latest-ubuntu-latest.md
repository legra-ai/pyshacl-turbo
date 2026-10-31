# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T21:31:33.920991+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `fa32f201ee3f7dcda7d51af5b0978efd086ef91f`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 13.855 | 13.622–14.302 | 64.50 | equal | 9.48× | — | — |
| pipeline_rdfs | 100 | python-reference | 131.399 | 130.632–131.736 | 47.41 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 33.848 | 33.241–38.942 | 44.28 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.485 | 23.141–23.580 | 65.45 | equal | 13.55× | — | — |
| pipeline_owlrl | 100 | python-reference | 318.194 | 315.478–320.205 | 47.70 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 50.846 | 50.131–54.980 | 45.38 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 337.204 | 332.067–459.084 | 73.88 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1298.888 | 1294.058–1396.088 | 52.67 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 104.203 | 102.136–107.943 | 70.03 | equal | 12.46× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2160.010 | 2143.351–2293.408 | 53.89 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 143.617 | 142.154–270.484 | 69.41 | equal | 15.04× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 439.055 | 429.408–526.813 | 80.29 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 47.320 | 47.154–48.572 | 42.71 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.609 | 5.481–5.902 | 63.31 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 55.545 | 55.331–56.471 | 76.58 | reference | — | — | — |
| literal-type | 32 | candidate | 6.221 | 6.086–6.510 | 86.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 116.819 | 116.339–118.784 | 110.83 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.461 | 9.304–9.615 | 110.83 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.595 | 11.340–11.760 | 218.99 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 145.521 | 144.347–146.807 | 218.99 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 24.275 | 24.010–24.509 | 330.20 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 390.078 | 388.191–430.357 | 330.20 | reference | — | — | — |
| literal-type | 512 | python-reference | 502.103 | 498.527–537.671 | 646.87 | reference | — | — | — |
| literal-type | 512 | candidate | 32.984 | 32.676–33.426 | 646.87 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 757.993 | 752.735–849.187 | 1055.14 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 44.172 | 43.676–46.878 | 1055.14 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 957.582 | 951.405–974.320 | 1650.12 | reference | — | — | — |
| literal-type | 1000 | candidate | 60.457 | 59.943–61.436 | 1650.12 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.2, rdflib-turbo 0.2.0a24

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
