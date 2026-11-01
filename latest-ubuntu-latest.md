# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-01T14:27:01.708875+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `9d5910e6b6b2e011859a8b3b8a5b7251cb5d4d5b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 13.580 | 13.447–14.292 | 64.37 | equal | 9.52× | — | — |
| pipeline_rdfs | 100 | python-reference | 129.275 | 128.566–131.102 | 47.27 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 34.596 | 34.174–41.147 | 43.79 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.295 | 23.061–23.498 | 65.34 | equal | 13.41× | — | — |
| pipeline_owlrl | 100 | python-reference | 312.404 | 311.089–316.647 | 47.61 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 51.071 | 49.535–58.028 | 44.98 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 332.565 | 317.717–426.310 | 73.64 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1291.230 | 1288.169–1386.130 | 52.87 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 104.248 | 102.125–105.209 | 69.77 | equal | 12.39× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2142.399 | 2133.912–2259.707 | 53.90 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 141.135 | 138.359–252.320 | 69.48 | equal | 15.18× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 433.569 | 423.406–502.462 | 80.06 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 47.406 | 47.252–49.172 | 42.82 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.563 | 5.359–5.677 | 63.64 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 54.401 | 53.919–54.866 | 76.57 | reference | — | — | — |
| literal-type | 32 | candidate | 6.130 | 6.048–6.496 | 86.20 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 115.291 | 114.415–116.756 | 110.95 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.344 | 9.290–9.455 | 110.95 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.467 | 11.274–11.770 | 218.96 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 143.268 | 141.301–145.394 | 218.96 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 24.161 | 24.006–24.575 | 330.29 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 387.649 | 386.953–426.805 | 330.29 | reference | — | — | — |
| literal-type | 512 | python-reference | 505.349 | 500.623–535.149 | 646.81 | reference | — | — | — |
| literal-type | 512 | candidate | 32.907 | 32.438–36.279 | 646.81 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 728.490 | 722.757–810.336 | 1055.14 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 43.789 | 43.096–44.648 | 1055.14 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 958.804 | 954.003–975.335 | 1650.17 | reference | — | — | — |
| literal-type | 1000 | candidate | 60.778 | 59.093–63.015 | 1650.17 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.5, rdflib-turbo 0.2.0a27

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
