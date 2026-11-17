# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-17T13:15:07.106667+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `e1fb11c010847556649f363b914b1421b7cb59ae`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 11.103 | 8.649–21.216 | 58.11 | equal | 7.50× | — | — |
| pipeline_rdfs | 100 | python-reference | 83.245 | 73.803–91.230 | 59.23 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 36.155 | 29.960–46.811 | 54.81 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 24.016 | 22.171–39.380 | 58.62 | equal | 8.62× | — | — |
| pipeline_owlrl | 100 | python-reference | 207.130 | 197.557–235.700 | 59.61 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 45.368 | 36.133–50.590 | 57.08 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 432.541 | 263.935–543.168 | 110.72 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 893.231 | 746.506–1470.337 | 64.73 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 50.568 | 47.893–80.143 | 63.78 | equal | 17.66× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1244.322 | 1158.511–1582.160 | 65.91 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 109.009 | 96.315–153.793 | 63.20 | equal | 11.41× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 576.086 | 434.743–654.287 | 120.31 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.520 | 24.756–40.895 | 47.61 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 8.323 | 4.887–10.392 | 55.89 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 40.673 | 28.622–46.246 | 47.61 | reference | — | — | — |
| literal-type | 32 | candidate | 8.238 | 6.591–10.456 | 55.83 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 71.191 | 61.509–98.825 | 47.73 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 11.239 | 7.215–14.173 | 56.22 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 15.795 | 10.988–20.967 | 56.33 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 91.637 | 77.820–102.760 | 47.69 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 22.430 | 17.480–29.349 | 58.81 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 290.714 | 233.384–425.454 | 49.25 | reference | — | — | — |
| literal-type | 512 | python-reference | 324.981 | 306.415–369.649 | 49.52 | reference | — | — | — |
| literal-type | 512 | candidate | 27.332 | 23.343–43.116 | 59.17 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 594.457 | 494.875–932.684 | 51.52 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 37.094 | 34.350–50.678 | 62.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 570.894 | 482.091–627.707 | 52.02 | reference | — | — | — |
| literal-type | 1000 | candidate | 46.169 | 40.896–55.287 | 62.59 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.2, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
