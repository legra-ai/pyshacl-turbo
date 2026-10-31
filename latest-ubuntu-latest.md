# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T22:23:52.443426+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `fa32f201ee3f7dcda7d51af5b0978efd086ef91f`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 11.724 | 11.676–12.638 | 64.55 | equal | 8.26× | — | — |
| pipeline_rdfs | 100 | python-reference | 96.888 | 95.072–100.978 | 47.39 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 25.626 | 25.143–29.830 | 44.08 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 21.762 | 21.316–22.577 | 65.52 | equal | 10.69× | — | — |
| pipeline_owlrl | 100 | python-reference | 232.733 | 229.570–241.904 | 47.62 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 39.494 | 38.621–43.068 | 45.29 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 257.529 | 254.239–343.869 | 73.88 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 974.814 | 947.939–1033.839 | 52.84 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 91.937 | 90.900–93.832 | 70.17 | equal | 10.60× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1599.298 | 1582.339–1697.561 | 53.86 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 137.888 | 136.441–196.352 | 70.36 | equal | 11.60× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 341.288 | 334.279–403.754 | 80.10 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 34.916 | 33.890–35.606 | 42.89 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.100 | 4.966–5.175 | 63.33 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 40.728 | 39.671–41.110 | 76.64 | reference | — | — | — |
| literal-type | 32 | candidate | 5.967 | 5.781–6.516 | 86.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 85.595 | 84.379–87.032 | 110.89 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.835 | 8.588–9.337 | 110.89 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.941 | 10.603–11.681 | 219.04 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 108.218 | 105.834–109.884 | 219.04 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 22.414 | 22.165–22.746 | 330.26 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 287.939 | 280.532–320.237 | 330.26 | reference | — | — | — |
| literal-type | 512 | python-reference | 368.679 | 364.768–401.806 | 646.80 | reference | — | — | — |
| literal-type | 512 | candidate | 32.240 | 31.317–32.870 | 646.80 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 541.279 | 535.227–627.859 | 1055.16 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 42.037 | 41.250–43.539 | 1055.16 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 709.698 | 704.944–717.539 | 1650.17 | reference | — | — | — |
| literal-type | 1000 | candidate | 57.052 | 56.175–58.879 | 1650.17 | different | — | logical_inplace_owlrl_different | — |
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
