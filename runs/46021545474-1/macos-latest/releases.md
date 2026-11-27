# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T15:56:16.345573+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `6bc80f5cba90a7a82f806685609ffcaa4bc4f1ba`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.284 | 6.707–8.334 | 58.05 | equal | 9.87× | — | — |
| pipeline_rdfs | 100 | python-reference | 71.881 | 62.164–81.660 | 59.34 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.319 | 22.236–30.521 | 54.70 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 21.251 | 16.997–26.218 | 58.55 | equal | 7.84× | — | — |
| pipeline_owlrl | 100 | python-reference | 166.615 | 162.211–184.562 | 59.64 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.762 | 31.257–40.428 | 56.84 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 208.996 | 191.595–276.974 | 109.03 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 739.827 | 698.249–1185.264 | 64.84 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 51.582 | 47.398–71.530 | 63.89 | equal | 14.34× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1196.600 | 1044.010–1362.697 | 65.94 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 109.835 | 104.032–164.126 | 63.09 | equal | 10.89× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 335.227 | 279.055–391.497 | 118.98 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 21.640 | 20.132–22.981 | 47.45 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.200 | 4.499–6.026 | 55.80 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 28.808 | 22.398–34.737 | 47.64 | reference | — | — | — |
| literal-type | 32 | candidate | 4.822 | 4.174–5.280 | 55.88 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 53.846 | 49.247–60.164 | 47.64 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.002 | 5.907–6.687 | 56.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.442 | 7.776–9.497 | 56.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 65.013 | 63.941–70.634 | 47.64 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.430 | 17.172–25.348 | 58.72 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 184.142 | 173.125–229.850 | 49.19 | reference | — | — | — |
| literal-type | 512 | python-reference | 230.898 | 221.986–303.248 | 49.47 | reference | — | — | — |
| literal-type | 512 | candidate | 22.140 | 19.933–26.420 | 59.02 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 325.174 | 317.695–677.163 | 51.39 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 26.935 | 26.437–34.302 | 62.05 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 457.601 | 423.948–622.399 | 51.89 | reference | — | — | — |
| literal-type | 1000 | candidate | 36.870 | 36.018–41.279 | 62.59 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.6, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
