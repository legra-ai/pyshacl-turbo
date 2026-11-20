# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-20T13:22:15.704967+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.272 | 9.104–9.439 | 76.59 | equal | 10.38× | — | — |
| pipeline_rdfs | 100 | python-reference | 96.247 | 95.790–99.604 | 55.54 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.624 | 27.014–31.784 | 54.06 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.229 | 20.127–20.554 | 77.36 | equal | 11.05× | — | — |
| pipeline_owlrl | 100 | python-reference | 223.460 | 221.810–226.918 | 55.99 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 42.801 | 41.861–48.550 | 54.18 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 275.639 | 266.787–368.108 | 82.21 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 994.525 | 988.553–1094.714 | 61.18 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 67.418 | 66.040–69.130 | 80.72 | equal | 14.75× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1521.694 | 1501.021–1630.593 | 62.16 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 125.814 | 124.311–127.350 | 81.32 | equal | 12.09× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 364.958 | 356.927–445.884 | 88.97 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3886.767 | 3777.376–4004.005 | 400.35 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 27658.072 | 27532.925–27829.104 | 126.65 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 769.872 | 762.404–1219.011 | 123.40 | equal | 35.93× | — | — |
| pipeline_owlrl | 10000 | python-reference | 15300.250 | 15177.940–15363.367 | 135.13 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1409.755 | 1372.109–1761.185 | 124.62 | equal | 10.85× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5460.566 | 5444.392–5552.213 | 458.74 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.726 | 32.355–32.931 | 162.42 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.933 | 4.877–5.152 | 162.42 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 5.529 | 5.404–5.643 | 195.31 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 37.998 | 37.541–38.227 | 195.31 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.204 | 8.090–8.284 | 234.01 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 82.053 | 81.127–82.451 | 234.01 | reference | — | — | — |
| literal-type | 128 | python-reference | 100.808 | 98.969–101.868 | 322.65 | reference | — | — | — |
| literal-type | 128 | candidate | 10.225 | 9.947–10.330 | 322.65 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 271.599 | 268.477–301.123 | 433.43 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.451 | 21.133–22.078 | 433.43 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 356.456 | 353.534–385.777 | 751.14 | reference | — | — | — |
| literal-type | 512 | candidate | 28.593 | 28.360–29.381 | 751.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 38.083 | 37.464–39.090 | 1159.40 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 511.562 | 509.014–588.508 | 1159.40 | reference | — | — | — |
| literal-type | 1000 | candidate | 52.253 | 52.012–52.911 | 1758.37 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 662.779 | 658.878–683.298 | 1758.37 | reference | — | — | — |
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
