# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-04T00:07:36.484627+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `b36b227b1766aee5397e3ff30b3076741e5fefdf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.767 | 9.498–10.338 | 66.18 | equal | 13.19× | — | — |
| pipeline_rdfs | 100 | python-reference | 128.834 | 127.897–131.464 | 47.25 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 33.607 | 32.908–38.865 | 44.21 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.193 | 22.582–23.252 | 66.69 | equal | 13.35× | — | — |
| pipeline_owlrl | 100 | python-reference | 309.573 | 309.084–318.543 | 47.65 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 49.542 | 49.057–53.707 | 45.42 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 326.039 | 314.515–415.923 | 73.93 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1287.154 | 1273.793–1340.433 | 52.79 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 68.048 | 67.562–69.928 | 71.27 | equal | 18.92× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2138.717 | 2116.297–2220.239 | 53.79 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 140.160 | 138.648–243.840 | 70.74 | equal | 15.26× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 436.074 | 418.904–501.433 | 80.27 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 47.603 | 46.690–49.084 | 42.97 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.409 | 5.331–5.587 | 64.95 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 54.673 | 54.309–55.340 | 76.72 | reference | — | — | — |
| literal-type | 32 | candidate | 6.125 | 6.006–7.539 | 86.35 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 114.456 | 113.627–115.507 | 110.85 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.362 | 9.205–9.488 | 110.85 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.405 | 11.288–11.742 | 219.01 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 144.382 | 143.302–145.837 | 219.01 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 24.084 | 23.893–24.497 | 330.50 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 386.727 | 381.336–419.693 | 330.50 | reference | — | — | — |
| literal-type | 512 | python-reference | 497.316 | 495.043–545.875 | 646.96 | reference | — | — | — |
| literal-type | 512 | candidate | 32.943 | 31.981–33.966 | 646.96 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 730.967 | 724.901–818.789 | 1055.30 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 43.551 | 42.834–44.706 | 1055.30 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 962.804 | 957.893–973.302 | 1650.23 | reference | — | — | — |
| literal-type | 1000 | candidate | 59.680 | 58.925–60.941 | 1650.23 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.10.0, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
