# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-03T22:59:04.716228+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `b36b227b1766aee5397e3ff30b3076741e5fefdf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.644 | 7.360–16.771 | 59.52 | equal | 6.78× | — | — |
| pipeline_rdfs | 100 | python-reference | 58.610 | 56.986–70.621 | 60.84 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 19.046 | 18.515–22.411 | 55.97 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.580 | 17.324–24.991 | 60.00 | equal | 7.94× | — | — |
| pipeline_owlrl | 100 | python-reference | 147.495 | 140.795–161.958 | 61.08 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 32.254 | 31.677–34.938 | 58.20 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 238.997 | 207.980–290.996 | 111.67 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 742.491 | 633.934–949.920 | 66.36 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 48.601 | 46.351–52.018 | 65.09 | equal | 15.28× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1092.547 | 1003.971–1137.277 | 67.44 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 109.931 | 94.955–135.139 | 64.28 | equal | 9.94× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 283.532 | 238.335–380.306 | 121.42 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 20.806 | 20.489–23.000 | 49.17 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.854 | 5.213–6.393 | 57.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 24.564 | 23.725–32.336 | 49.16 | reference | — | — | — |
| literal-type | 32 | candidate | 5.823 | 5.341–7.743 | 57.16 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 56.891 | 52.033–67.198 | 49.19 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.362 | 7.127–7.927 | 57.42 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.078 | 8.990–9.351 | 57.48 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 71.456 | 67.748–88.271 | 49.12 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 18.934 | 18.247–19.854 | 60.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 184.796 | 173.485–196.839 | 50.77 | reference | — | — | — |
| literal-type | 512 | python-reference | 259.648 | 220.336–291.682 | 50.97 | reference | — | — | — |
| literal-type | 512 | candidate | 26.399 | 25.867–27.535 | 60.38 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 342.537 | 319.733–395.098 | 53.00 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 33.699 | 31.973–37.323 | 63.33 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 450.772 | 427.810–522.553 | 53.47 | reference | — | — | — |
| literal-type | 1000 | candidate | 45.695 | 42.400–54.828 | 63.86 | different | — | logical_inplace_owlrl_different | — |
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
