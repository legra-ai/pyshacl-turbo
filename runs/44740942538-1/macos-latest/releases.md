# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-20T13:26:28.054555+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 11.363 | 8.329–11.929 | 58.00 | equal | 5.29× | — | — |
| pipeline_rdfs | 100 | python-reference | 60.153 | 59.301–71.790 | 59.33 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.085 | 19.469–23.390 | 54.83 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.041 | 15.530–17.104 | 58.62 | equal | 10.82× | — | — |
| pipeline_owlrl | 100 | python-reference | 173.509 | 148.880–203.922 | 59.70 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 32.595 | 28.929–35.331 | 57.09 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 198.922 | 183.741–271.832 | 110.86 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 760.060 | 665.770–854.541 | 64.83 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 50.001 | 47.749–55.109 | 63.72 | equal | 15.20× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1319.919 | 1197.217–1429.818 | 65.89 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 93.427 | 88.737–96.861 | 63.02 | equal | 14.13× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 327.993 | 262.656–439.475 | 120.78 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3517.342 | 3277.910–4031.286 | 690.47 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 27734.856 | 24573.813–28297.492 | 140.52 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 590.511 | 530.103–1005.680 | 128.30 | equal | 46.97× | — | — |
| pipeline_owlrl | 10000 | python-reference | 14896.396 | 12332.524–16975.954 | 149.56 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 953.470 | 857.885–1248.153 | 121.81 | equal | 15.62× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 3364.213 | 3173.571–3430.113 | 795.34 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 21.418 | 21.333–21.908 | 47.75 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.511 | 3.481–3.576 | 55.95 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 3.902 | 3.866–3.974 | 55.80 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 23.000 | 22.058–23.973 | 47.67 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.162 | 5.788–6.377 | 56.19 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 50.081 | 49.187–54.544 | 47.67 | reference | — | — | — |
| literal-type | 128 | python-reference | 65.171 | 63.660–68.442 | 47.75 | reference | — | — | — |
| literal-type | 128 | candidate | 8.800 | 8.189–9.317 | 56.28 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 226.116 | 203.681–251.182 | 49.28 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.992 | 17.980–22.520 | 58.70 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 368.235 | 302.354–396.645 | 49.61 | reference | — | — | — |
| literal-type | 512 | candidate | 26.500 | 24.080–41.861 | 59.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 51.012 | 33.196–61.147 | 62.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 510.301 | 440.847–697.858 | 51.58 | reference | — | — | — |
| literal-type | 1000 | candidate | 42.236 | 35.717–85.034 | 62.55 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 457.033 | 444.940–495.355 | 51.97 | reference | — | — | — |
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
