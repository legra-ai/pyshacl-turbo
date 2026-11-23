# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-23T15:10:34.068906+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.320 | 6.742–17.273 | 57.98 | equal | 11.20× | — | — |
| pipeline_rdfs | 100 | python-reference | 104.368 | 92.252–128.554 | 59.31 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 23.885 | 20.488–30.761 | 54.80 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 14.802 | 13.910–15.909 | 58.58 | equal | 18.07× | — | — |
| pipeline_owlrl | 100 | python-reference | 267.497 | 189.861–364.433 | 59.64 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.463 | 31.059–39.388 | 56.92 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 217.561 | 178.780–302.995 | 110.95 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 700.630 | 582.818–1047.132 | 64.89 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 44.420 | 42.815–49.986 | 63.58 | equal | 15.77× | — | — |
| pipeline_owlrl | 1000 | python-reference | 958.274 | 907.172–1113.418 | 65.97 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 90.431 | 79.965–115.830 | 63.23 | equal | 10.60× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 231.498 | 223.762–268.374 | 120.62 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 2936.026 | 2745.012–3478.300 | 693.34 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 23076.103 | 18401.253–23372.643 | 140.45 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 573.970 | 524.261–800.832 | 128.33 | equal | 40.20× | — | — |
| pipeline_owlrl | 10000 | python-reference | 11196.134 | 11132.662–11738.804 | 149.56 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1264.432 | 1164.894–1548.587 | 121.27 | equal | 8.85× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5719.135 | 4955.921–5920.027 | 785.12 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 22.538 | 21.736–24.585 | 47.62 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.237 | 3.634–4.462 | 55.84 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.944 | 4.563–5.400 | 55.89 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 37.021 | 30.188–49.550 | 47.59 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.824 | 6.952–12.730 | 56.22 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 58.078 | 49.304–63.804 | 47.61 | reference | — | — | — |
| literal-type | 128 | python-reference | 71.203 | 66.803–74.858 | 47.55 | reference | — | — | — |
| literal-type | 128 | candidate | 9.507 | 8.666–13.347 | 56.20 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 220.591 | 195.564–251.920 | 49.25 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.944 | 17.494–25.304 | 58.75 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 252.283 | 222.747–390.610 | 49.50 | reference | — | — | — |
| literal-type | 512 | candidate | 24.856 | 22.802–26.066 | 59.06 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 30.415 | 28.019–38.362 | 62.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 363.714 | 356.625–449.246 | 51.41 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.206 | 37.481–59.411 | 62.64 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 515.822 | 457.938–596.519 | 52.05 | reference | — | — | — |
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
