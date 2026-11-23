# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-23T15:03:08.234250+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.282 | 7.159–7.427 | 76.54 | equal | 9.40× | — | — |
| pipeline_rdfs | 100 | python-reference | 68.466 | 67.362–70.911 | 55.64 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.160 | 20.915–25.133 | 54.20 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.321 | 16.067–16.519 | 77.32 | equal | 9.90× | — | — |
| pipeline_owlrl | 100 | python-reference | 161.527 | 160.649–162.914 | 55.87 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 32.918 | 32.239–35.839 | 54.18 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 216.752 | 211.689–335.210 | 82.35 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 708.343 | 700.991–803.084 | 61.08 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 54.241 | 52.994–54.738 | 80.68 | equal | 13.06× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1121.913 | 1112.131–1221.403 | 62.18 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 101.439 | 100.553–103.646 | 81.37 | equal | 11.06× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 293.647 | 283.975–378.181 | 89.08 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3602.846 | 3447.019–3682.145 | 400.48 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 19335.798 | 19283.064–19539.679 | 126.55 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 657.250 | 638.763–1061.063 | 123.84 | equal | 29.42× | — | — |
| pipeline_owlrl | 10000 | python-reference | 11442.654 | 11323.728–11550.519 | 135.09 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1209.568 | 1168.533–1767.518 | 124.80 | equal | 9.46× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5051.834 | 5011.087–5284.227 | 458.54 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 23.972 | 23.633–24.579 | 169.31 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.172 | 4.062–4.248 | 169.31 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.440 | 4.380–4.614 | 202.28 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.620 | 27.218–27.924 | 202.28 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.638 | 6.589–6.799 | 240.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 59.307 | 58.578–60.438 | 240.92 | reference | — | — | — |
| literal-type | 128 | python-reference | 74.609 | 72.906–75.791 | 329.41 | reference | — | — | — |
| literal-type | 128 | candidate | 8.140 | 8.040–8.206 | 329.41 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 204.883 | 201.473–241.244 | 440.11 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.317 | 16.959–18.458 | 440.11 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 256.481 | 254.273–295.042 | 753.31 | reference | — | — | — |
| literal-type | 512 | candidate | 23.191 | 22.968–23.462 | 753.31 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 31.203 | 30.759–31.754 | 1159.23 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 381.650 | 373.962–454.439 | 1159.23 | reference | — | — | — |
| literal-type | 1000 | candidate | 42.874 | 42.431–43.327 | 1753.58 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 504.781 | 492.677–512.033 | 1753.58 | reference | — | — | — |
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
