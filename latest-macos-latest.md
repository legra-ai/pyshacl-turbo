# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-04T00:51:15.261660+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `b36b227b1766aee5397e3ff30b3076741e5fefdf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.168 | 7.782–15.535 | 59.55 | equal | 6.85× | — | — |
| pipeline_rdfs | 100 | python-reference | 62.774 | 61.627–69.381 | 60.91 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.776 | 20.202–30.067 | 55.88 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.540 | 18.052–18.944 | 60.20 | equal | 8.09× | — | — |
| pipeline_owlrl | 100 | python-reference | 149.932 | 141.346–171.992 | 61.19 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 32.995 | 29.794–35.890 | 58.06 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 218.215 | 181.063–267.539 | 110.36 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 753.972 | 640.779–2637.966 | 66.45 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 48.356 | 47.163–55.372 | 65.20 | equal | 15.59× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1133.801 | 1017.259–1255.388 | 67.59 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 101.432 | 99.110–103.763 | 64.41 | equal | 11.18× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 327.994 | 281.668–393.334 | 120.11 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 20.857 | 19.752–23.283 | 49.16 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.222 | 3.901–4.400 | 57.22 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.738 | 22.447–23.874 | 49.19 | reference | — | — | — |
| literal-type | 32 | candidate | 6.087 | 5.469–7.843 | 57.22 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 47.288 | 46.175–54.183 | 49.14 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.480 | 6.388–6.597 | 57.52 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.412 | 8.010–13.390 | 57.59 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 58.199 | 58.057–58.725 | 49.12 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 18.956 | 18.381–19.320 | 60.03 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 199.256 | 183.604–259.589 | 50.80 | reference | — | — | — |
| literal-type | 512 | python-reference | 265.955 | 250.892–270.607 | 51.11 | reference | — | — | — |
| literal-type | 512 | candidate | 26.882 | 24.433–29.914 | 60.42 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 330.775 | 298.759–372.817 | 52.98 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 29.380 | 28.789–33.298 | 63.45 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 400.033 | 387.107–448.533 | 53.56 | reference | — | — | — |
| literal-type | 1000 | candidate | 42.464 | 40.883–52.704 | 63.92 | different | — | logical_inplace_owlrl_different | — |
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
