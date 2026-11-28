# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T13:53:47.397826+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `5be2fd5b65a8200bb299b744f781034fa902baff`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.673 | 8.700–13.986 | 58.05 | equal | 7.89× | — | — |
| pipeline_rdfs | 100 | python-reference | 76.353 | 68.028–83.901 | 59.33 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 35.853 | 21.471–45.977 | 54.42 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 25.757 | 22.006–31.755 | 58.64 | equal | 6.81× | — | — |
| pipeline_owlrl | 100 | python-reference | 175.287 | 155.098–251.519 | 59.64 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.670 | 31.892–35.122 | 56.89 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 300.616 | 233.828–473.802 | 110.78 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 762.352 | 695.086–797.498 | 64.84 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 53.717 | 49.157–59.846 | 63.69 | equal | 14.19× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1215.133 | 1104.695–1409.579 | 65.91 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 103.409 | 88.054–108.575 | 63.08 | equal | 11.75× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 298.512 | 265.801–338.081 | 116.36 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3649.050 | 3213.008–4383.198 | 683.73 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 15736.275 | 15466.067–26502.049 | 140.55 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 461.373 | 427.418–658.084 | 127.81 | equal | 34.11× | — | — |
| pipeline_owlrl | 10000 | python-reference | 10741.284 | 9779.846–11336.146 | 149.55 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1063.987 | 823.039–1303.406 | 121.91 | equal | 10.10× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 4491.529 | 3733.488–5325.265 | 779.48 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 20.816 | 20.162–24.795 | 47.61 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.170 | 4.094–4.263 | 55.80 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 5.800 | 5.053–7.186 | 55.89 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 24.387 | 23.345–24.854 | 47.64 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.803 | 6.824–8.499 | 56.17 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 51.836 | 47.075–53.897 | 47.67 | reference | — | — | — |
| literal-type | 128 | python-reference | 60.044 | 57.880–64.591 | 47.64 | reference | — | — | — |
| literal-type | 128 | candidate | 7.128 | 7.106–7.195 | 56.16 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 189.028 | 160.061–201.575 | 49.33 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.430 | 17.017–22.452 | 58.75 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 231.726 | 225.240–278.055 | 49.69 | reference | — | — | — |
| literal-type | 512 | candidate | 22.478 | 21.680–29.025 | 59.02 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 30.622 | 28.877–39.282 | 62.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 352.595 | 332.959–421.176 | 51.61 | reference | — | — | — |
| literal-type | 1000 | candidate | 51.926 | 40.329–78.161 | 62.56 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 463.195 | 444.970–473.264 | 52.03 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.11, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
