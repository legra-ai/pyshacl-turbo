# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-01T13:21:43.398871+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `9d5910e6b6b2e011859a8b3b8a5b7251cb5d4d5b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.641 | 8.260–10.191 | 59.31 | equal | 7.04× | — | — |
| pipeline_rdfs | 100 | python-reference | 60.841 | 53.044–73.354 | 60.83 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 17.613 | 16.609–19.568 | 55.94 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.222 | 14.935–16.257 | 59.53 | equal | 8.41× | — | — |
| pipeline_owlrl | 100 | python-reference | 127.965 | 127.018–129.854 | 61.02 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 27.453 | 26.069–31.791 | 58.12 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 188.239 | 160.319–250.428 | 111.92 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 582.489 | 557.846–602.309 | 66.30 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 64.413 | 61.306–78.848 | 66.00 | equal | 9.04× | — | — |
| pipeline_owlrl | 1000 | python-reference | 908.711 | 878.038–947.840 | 67.36 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 86.662 | 86.208–92.253 | 64.22 | equal | 10.49× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 217.785 | 213.889–263.969 | 122.17 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 21.972 | 18.710–27.815 | 49.17 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.795 | 3.759–3.880 | 56.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.071 | 21.914–23.304 | 49.16 | reference | — | — | — |
| literal-type | 32 | candidate | 4.253 | 4.211–4.348 | 56.98 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 45.996 | 45.685–47.792 | 49.02 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.428 | 6.400–6.523 | 57.25 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.902 | 7.852–7.967 | 57.30 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 59.502 | 57.362–69.812 | 49.09 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.375 | 16.254–17.677 | 59.80 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 155.476 | 153.377–174.083 | 50.66 | reference | — | — | — |
| literal-type | 512 | python-reference | 210.161 | 199.090–251.109 | 51.05 | reference | — | — | — |
| literal-type | 512 | candidate | 21.624 | 21.427–23.330 | 60.02 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 313.931 | 286.290–368.129 | 53.02 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 28.425 | 28.323–28.833 | 63.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 387.349 | 381.823–449.867 | 53.50 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.668 | 38.518–39.304 | 63.53 | different | — | logical_inplace_owlrl_different | — |
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
