# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T21:26:19.468492+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `fa32f201ee3f7dcda7d51af5b0978efd086ef91f`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.467 | 8.265–13.362 | 59.23 | equal | 5.61× | — | — |
| pipeline_rdfs | 100 | python-reference | 53.094 | 52.261–54.589 | 60.80 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 17.275 | 16.792–19.173 | 55.53 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 14.942 | 14.659–15.099 | 59.73 | equal | 8.86× | — | — |
| pipeline_owlrl | 100 | python-reference | 132.433 | 129.672–153.206 | 61.09 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 26.812 | 25.958–28.024 | 57.81 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 160.613 | 158.759–208.022 | 107.31 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 551.684 | 546.999–597.663 | 66.28 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 60.855 | 60.489–61.581 | 66.06 | equal | 9.07× | — | — |
| pipeline_owlrl | 1000 | python-reference | 875.492 | 871.264–1013.230 | 67.42 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 86.226 | 85.807–86.780 | 64.31 | equal | 10.15× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 214.356 | 211.342–264.760 | 117.34 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 18.955 | 18.859–19.222 | 49.14 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.774 | 3.743–3.840 | 57.11 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.117 | 21.838–22.361 | 49.14 | reference | — | — | — |
| literal-type | 32 | candidate | 4.248 | 4.222–4.329 | 57.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 46.263 | 46.008–47.100 | 49.17 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.370 | 6.262–6.697 | 57.36 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.810 | 8.719–9.075 | 57.41 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 57.800 | 57.483–58.337 | 49.02 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.270 | 16.205–16.426 | 60.02 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 154.796 | 152.566–175.260 | 50.75 | reference | — | — | — |
| literal-type | 512 | python-reference | 203.360 | 202.047–252.047 | 51.05 | reference | — | — | — |
| literal-type | 512 | candidate | 21.553 | 21.496–22.015 | 60.22 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 301.693 | 298.275–346.996 | 52.95 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 28.302 | 28.240–28.874 | 63.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 383.781 | 382.370–432.552 | 53.53 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.647 | 38.370–43.137 | 63.75 | different | — | logical_inplace_owlrl_different | — |
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
