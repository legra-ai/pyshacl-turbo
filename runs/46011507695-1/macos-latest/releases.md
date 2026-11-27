# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T14:26:02.852544+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `8adb778f823fb5b77c9c45df2ccdd5b3afc802ab`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.312 | 7.635–15.271 | 58.02 | equal | 6.67× | — | — |
| pipeline_rdfs | 100 | python-reference | 68.825 | 64.548–75.966 | 59.34 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.377 | 20.675–28.597 | 54.44 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.188 | 16.536–25.020 | 58.66 | equal | 9.93× | — | — |
| pipeline_owlrl | 100 | python-reference | 170.756 | 157.579–181.890 | 59.67 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 49.624 | 40.985–73.036 | 56.64 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 263.054 | 205.457–328.001 | 107.14 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 867.794 | 645.170–940.933 | 64.83 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 51.330 | 49.722–57.156 | 63.64 | equal | 16.91× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1235.785 | 1138.448–1520.685 | 65.92 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 90.957 | 83.766–106.284 | 62.94 | equal | 13.59× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 298.736 | 244.689–368.294 | 119.08 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3734.614 | 3526.838–4172.638 | 669.25 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 23832.619 | 21389.523–26760.581 | 140.36 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 570.051 | 441.997–749.131 | 128.86 | equal | 41.81× | — | — |
| pipeline_owlrl | 10000 | python-reference | 11323.683 | 9743.560–14427.387 | 149.45 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 847.700 | 841.398–1383.213 | 121.84 | equal | 13.36× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 3833.355 | 3370.537–3979.386 | 773.78 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 19.974 | 19.465–22.621 | 47.66 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.657 | 3.540–4.432 | 55.86 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.026 | 3.948–4.284 | 55.92 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.706 | 22.159–25.495 | 47.67 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 5.978 | 5.851–7.883 | 56.12 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 52.736 | 51.133–56.309 | 47.66 | reference | — | — | — |
| literal-type | 128 | python-reference | 70.332 | 60.023–80.439 | 47.66 | reference | — | — | — |
| literal-type | 128 | candidate | 7.517 | 7.046–8.940 | 56.19 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 169.255 | 161.307–194.272 | 49.27 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 14.430 | 14.317–15.597 | 58.80 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 239.196 | 201.946–271.224 | 49.55 | reference | — | — | — |
| literal-type | 512 | candidate | 21.535 | 20.665–23.147 | 59.02 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 32.732 | 25.911–74.685 | 62.05 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 318.342 | 309.713–361.011 | 51.48 | reference | — | — | — |
| literal-type | 1000 | candidate | 36.436 | 35.543–53.472 | 62.61 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 478.458 | 451.932–523.829 | 52.05 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.5, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
