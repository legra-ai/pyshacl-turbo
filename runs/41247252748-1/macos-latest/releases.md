# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T23:20:04.889334+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `a568c877783ff1b56f97275152191c5d38417149`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 13.552 | 10.288–17.530 | 59.39 | equal | 4.01× | — | — |
| pipeline_rdfs | 100 | python-reference | 54.381 | 53.372–58.507 | 60.89 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 17.371 | 17.027–23.667 | 55.97 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.421 | 15.091–17.564 | 59.78 | equal | 8.59× | — | — |
| pipeline_owlrl | 100 | python-reference | 132.517 | 128.362–137.309 | 61.16 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 27.719 | 26.683–30.039 | 58.28 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 205.261 | 161.833–253.820 | 110.98 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 574.734 | 556.668–645.968 | 66.39 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 73.674 | 69.217–88.876 | 65.78 | equal | 7.80× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1033.773 | 1008.201–1441.271 | 67.41 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 119.386 | 97.134–154.347 | 63.98 | equal | 8.66× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 304.974 | 265.372–479.147 | 118.58 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 25.007 | 24.717–27.221 | 49.16 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.285 | 4.899–6.358 | 57.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 25.541 | 24.439–26.650 | 49.09 | reference | — | — | — |
| literal-type | 32 | candidate | 5.035 | 4.581–7.942 | 57.19 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 52.867 | 48.111–63.539 | 49.05 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.573 | 8.271–11.955 | 57.38 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.508 | 8.608–14.293 | 57.55 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 88.839 | 69.411–94.321 | 49.16 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 20.018 | 18.212–21.036 | 60.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 181.050 | 176.494–204.515 | 50.70 | reference | — | — | — |
| literal-type | 512 | python-reference | 270.805 | 239.552–319.570 | 50.98 | reference | — | — | — |
| literal-type | 512 | candidate | 25.815 | 24.425–27.671 | 60.39 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 422.761 | 381.844–554.682 | 53.02 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 36.098 | 32.852–38.918 | 63.30 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 488.926 | 467.370–546.470 | 53.48 | reference | — | — | — |
| literal-type | 1000 | candidate | 47.434 | 45.453–62.687 | 63.86 | different | — | logical_inplace_owlrl_different | — |
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
