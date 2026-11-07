# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-07T22:35:52.278488+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `ae8e55f7ecd688d7a1fafa4a73e42c8aab2fba43`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.548 | 9.426–9.826 | 68.93 | equal | 13.64× | — | — |
| pipeline_rdfs | 100 | python-reference | 130.227 | 129.397–133.523 | 48.41 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 32.769 | 31.882–38.292 | 46.97 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 22.571 | 22.486–23.064 | 69.45 | equal | 14.05× | — | — |
| pipeline_owlrl | 100 | python-reference | 317.173 | 314.220–319.704 | 48.87 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 48.385 | 47.481–51.718 | 46.91 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 324.318 | 313.352–423.409 | 75.14 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1273.931 | 1265.865–1361.411 | 53.26 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 66.832 | 66.627–69.735 | 71.96 | equal | 19.06× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2181.042 | 2163.632–2304.259 | 54.74 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 141.781 | 140.534–142.290 | 72.59 | equal | 15.38× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 420.084 | 414.069–501.593 | 81.58 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 47.807 | 47.649–48.024 | 44.03 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.223 | 5.141–5.272 | 66.70 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 55.452 | 55.274–56.518 | 77.90 | reference | — | — | — |
| literal-type | 32 | candidate | 5.865 | 5.785–5.905 | 87.40 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 115.620 | 114.596–116.742 | 112.03 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.976 | 8.824–9.062 | 112.03 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.214 | 10.996–11.308 | 220.25 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 144.459 | 143.475–146.316 | 220.25 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 23.927 | 23.675–24.400 | 331.47 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 390.406 | 387.517–417.767 | 331.47 | reference | — | — | — |
| literal-type | 512 | python-reference | 493.173 | 491.519–522.582 | 647.89 | reference | — | — | — |
| literal-type | 512 | candidate | 32.548 | 32.044–32.719 | 647.89 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 750.048 | 743.492–840.423 | 1056.20 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 43.320 | 42.944–43.990 | 1056.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 952.814 | 944.963–959.332 | 1651.34 | reference | — | — | — |
| literal-type | 1000 | candidate | 59.688 | 59.004–72.456 | 1651.34 | different | — | logical_inplace_owlrl_different | — |
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
