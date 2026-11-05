# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-05T12:51:29.872908+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `b36b227b1766aee5397e3ff30b3076741e5fefdf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.120 | 7.203–11.580 | 59.56 | equal | 8.06× | — | — |
| pipeline_rdfs | 100 | python-reference | 73.550 | 71.762–77.734 | 61.02 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 23.246 | 22.323–31.926 | 55.81 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.041 | 17.386–22.796 | 60.11 | equal | 10.43× | — | — |
| pipeline_owlrl | 100 | python-reference | 188.137 | 148.499–208.413 | 61.23 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 30.585 | 29.257–33.141 | 57.98 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 240.846 | 197.155–396.162 | 110.00 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 773.816 | 693.387–1033.950 | 66.47 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 62.240 | 48.177–75.029 | 65.28 | equal | 12.43× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1161.820 | 1062.911–1375.508 | 67.62 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 131.930 | 120.832–166.605 | 64.62 | equal | 8.81× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 301.078 | 283.123–348.552 | 120.12 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3365.480 | 2953.874–3720.847 | 682.91 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 25384.572 | 19918.461–39714.593 | 142.12 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 624.977 | 515.435–834.201 | 129.67 | equal | 40.62× | — | — |
| pipeline_owlrl | 10000 | python-reference | 12000.785 | 11335.038–12473.151 | 151.23 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1652.526 | 1202.689–2260.764 | 122.61 | equal | 7.26× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5134.660 | 4767.555–6054.725 | 785.50 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 22.621 | 20.972–40.319 | 49.19 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 6.374 | 5.114–11.602 | 57.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 7.208 | 5.880–10.592 | 57.11 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 28.398 | 27.887–33.416 | 49.19 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.437 | 8.883–11.463 | 57.48 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 69.990 | 63.158–80.129 | 49.25 | reference | — | — | — |
| literal-type | 128 | python-reference | 79.796 | 77.627–82.145 | 49.16 | reference | — | — | — |
| literal-type | 128 | candidate | 9.901 | 9.523–14.596 | 57.64 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 215.559 | 190.131–254.642 | 50.83 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 23.585 | 21.784–26.209 | 60.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 287.563 | 269.663–367.859 | 51.12 | reference | — | — | — |
| literal-type | 512 | candidate | 30.741 | 30.187–36.523 | 60.38 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 47.560 | 39.473–51.915 | 63.38 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 387.069 | 371.482–479.983 | 53.06 | reference | — | — | — |
| literal-type | 1000 | candidate | 63.039 | 52.479–82.818 | 63.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 502.961 | 475.588–701.494 | 53.56 | reference | — | — | — |
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
