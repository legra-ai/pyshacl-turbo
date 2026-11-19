# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-19T13:28:27.100131+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.413 | 9.348–9.621 | 76.59 | equal | 10.23× | — | — |
| pipeline_rdfs | 100 | python-reference | 96.314 | 95.836–100.445 | 55.69 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 28.653 | 28.219–33.585 | 54.11 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.840 | 20.444–20.984 | 77.30 | equal | 10.77× | — | — |
| pipeline_owlrl | 100 | python-reference | 224.426 | 223.476–260.266 | 55.84 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 42.949 | 41.865–45.374 | 54.30 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 277.357 | 273.325–383.395 | 82.48 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1026.510 | 1000.977–1117.663 | 61.16 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 66.217 | 65.060–67.755 | 80.50 | equal | 15.50× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1557.120 | 1527.300–1646.794 | 62.20 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 126.649 | 125.174–130.912 | 81.39 | equal | 12.29× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 381.578 | 370.351–471.007 | 88.89 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.729 | 32.500–32.881 | 52.27 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.017 | 4.907–6.157 | 74.37 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 38.219 | 37.899–38.369 | 86.14 | reference | — | — | — |
| literal-type | 32 | candidate | 5.760 | 5.630–5.991 | 95.64 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 80.113 | 79.432–95.241 | 120.52 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.283 | 8.048–8.430 | 120.52 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.197 | 10.066–10.592 | 228.50 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 101.722 | 101.158–101.963 | 228.50 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.429 | 21.090–21.487 | 339.79 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 272.610 | 270.747–306.177 | 339.79 | reference | — | — | — |
| literal-type | 512 | python-reference | 352.931 | 348.841–390.824 | 656.32 | reference | — | — | — |
| literal-type | 512 | candidate | 29.081 | 28.783–30.692 | 656.32 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 515.502 | 511.759–599.962 | 1064.57 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 38.420 | 38.130–40.252 | 1064.57 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 667.393 | 662.334–676.108 | 1659.48 | reference | — | — | — |
| literal-type | 1000 | candidate | 53.063 | 52.595–53.808 | 1659.48 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
