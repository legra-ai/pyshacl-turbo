# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-08T11:40:19.058082+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `ae8e55f7ecd688d7a1fafa4a73e42c8aab2fba43`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.807 | 6.934–16.875 | 59.55 | equal | 7.25× | — | — |
| pipeline_rdfs | 100 | python-reference | 56.614 | 53.106–64.943 | 60.84 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 17.090 | 16.675–19.487 | 55.61 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.677 | 15.131–19.585 | 60.16 | equal | 8.38× | — | — |
| pipeline_owlrl | 100 | python-reference | 131.325 | 128.870–134.292 | 61.11 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 29.564 | 29.029–38.238 | 57.75 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 201.202 | 180.332–276.818 | 107.11 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 565.166 | 552.565–658.149 | 66.30 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 42.603 | 41.411–54.292 | 64.94 | equal | 13.27× | — | — |
| pipeline_owlrl | 1000 | python-reference | 937.499 | 898.881–1648.309 | 67.44 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 88.493 | 87.284–102.558 | 64.39 | equal | 10.59× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 261.232 | 216.051–334.723 | 117.47 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 2730.499 | 2599.806–3267.935 | 643.47 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 21952.285 | 17516.698–32355.536 | 141.95 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 456.383 | 427.602–532.731 | 129.84 | equal | 48.10× | — | — |
| pipeline_owlrl | 10000 | python-reference | 9660.439 | 9191.063–11817.202 | 151.09 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 997.118 | 900.042–1243.613 | 122.47 | equal | 9.69× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 3638.718 | 3440.118–5196.341 | 743.92 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.542 | 21.932–29.416 | 49.17 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.887 | 5.409–7.101 | 57.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 6.075 | 5.366–8.744 | 57.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 31.035 | 26.905–36.139 | 49.19 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 14.123 | 11.975–22.411 | 57.41 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 92.507 | 70.302–112.945 | 49.22 | reference | — | — | — |
| literal-type | 128 | python-reference | 100.410 | 96.285–117.528 | 49.16 | reference | — | — | — |
| literal-type | 128 | candidate | 16.727 | 10.339–21.458 | 57.53 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 282.182 | 230.896–326.295 | 50.80 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 25.417 | 18.950–36.623 | 60.08 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 266.671 | 235.947–295.537 | 51.08 | reference | — | — | — |
| literal-type | 512 | candidate | 31.096 | 25.363–41.616 | 60.34 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 38.996 | 30.755–49.965 | 63.31 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 399.378 | 376.457–533.966 | 52.97 | reference | — | — | — |
| literal-type | 1000 | candidate | 45.429 | 42.886–48.482 | 63.86 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 466.804 | 398.695–523.747 | 53.52 | reference | — | — | — |
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
