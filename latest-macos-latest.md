# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-26T14:27:07.279777+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.842 | 8.737–13.559 | 57.95 | equal | 7.14× | — | — |
| pipeline_rdfs | 100 | python-reference | 63.124 | 59.271–73.304 | 59.16 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 25.059 | 22.407–46.839 | 54.89 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.785 | 17.821–22.158 | 58.59 | equal | 8.24× | — | — |
| pipeline_owlrl | 100 | python-reference | 154.866 | 145.657–225.426 | 59.61 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.772 | 33.706–38.533 | 56.84 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 234.590 | 189.898–302.652 | 110.08 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 754.269 | 650.401–867.745 | 64.84 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 60.811 | 53.337–73.449 | 63.80 | equal | 12.40× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1187.571 | 1156.953–1350.768 | 65.94 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 115.215 | 109.515–196.070 | 63.11 | equal | 10.31× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 329.056 | 291.282–369.596 | 119.67 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 4101.614 | 3608.728–4288.093 | 690.48 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 27433.196 | 22894.624–33690.202 | 140.45 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 604.940 | 532.235–946.494 | 128.81 | equal | 45.35× | — | — |
| pipeline_owlrl | 10000 | python-reference | 12820.463 | 11507.394–17912.785 | 149.53 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1286.809 | 1022.566–1761.855 | 121.70 | equal | 9.96× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5391.005 | 4992.410–6002.548 | 775.09 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 26.607 | 22.250–29.611 | 47.38 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.009 | 4.601–6.303 | 55.84 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 7.202 | 5.023–9.169 | 55.81 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 36.699 | 28.808–45.730 | 47.61 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.280 | 7.153–8.931 | 56.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 64.561 | 58.477–102.746 | 47.47 | reference | — | — | — |
| literal-type | 128 | python-reference | 73.669 | 71.603–80.293 | 47.64 | reference | — | — | — |
| literal-type | 128 | candidate | 10.766 | 8.390–14.445 | 56.19 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 228.692 | 213.699–246.020 | 49.25 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.172 | 16.407–18.429 | 58.70 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 352.237 | 281.305–440.907 | 49.42 | reference | — | — | — |
| literal-type | 512 | candidate | 27.342 | 23.580–28.783 | 58.95 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 33.938 | 31.392–39.678 | 61.95 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 418.169 | 373.374–489.134 | 51.41 | reference | — | — | — |
| literal-type | 1000 | candidate | 47.760 | 43.682–54.622 | 62.48 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 477.300 | 438.988–678.529 | 52.11 | reference | — | — | — |
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
