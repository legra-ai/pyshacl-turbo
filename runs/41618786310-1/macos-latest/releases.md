# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-03T13:25:06.805909+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `8681c940fb816f864f3b2452fa760faed78e574c`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.395 | 8.581–13.734 | 59.41 | equal | 8.02× | — | — |
| pipeline_rdfs | 100 | python-reference | 75.375 | 65.347–89.897 | 60.77 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.896 | 17.068–25.612 | 55.83 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 19.737 | 16.124–27.414 | 60.11 | equal | 9.32× | — | — |
| pipeline_owlrl | 100 | python-reference | 184.033 | 149.486–266.047 | 61.06 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 35.365 | 31.783–40.709 | 58.03 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 233.003 | 221.475–370.623 | 111.36 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 775.781 | 714.448–919.519 | 66.27 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 58.095 | 54.875–66.183 | 65.28 | equal | 13.35× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1310.469 | 1165.054–1503.213 | 67.39 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 118.620 | 113.179–163.828 | 64.33 | equal | 11.05× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 349.742 | 300.700–427.736 | 121.12 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 23.843 | 22.552–25.379 | 48.89 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 7.637 | 4.872–10.719 | 56.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.226 | 25.546–32.995 | 48.97 | reference | — | — | — |
| literal-type | 32 | candidate | 7.632 | 5.203–12.975 | 57.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 87.369 | 57.109–123.878 | 49.16 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.216 | 8.503–16.192 | 57.45 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.431 | 10.157–11.010 | 57.42 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 72.136 | 69.770–80.187 | 49.02 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.633 | 21.195–26.207 | 60.05 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 205.361 | 202.169–245.280 | 50.77 | reference | — | — | — |
| literal-type | 512 | python-reference | 323.504 | 266.295–455.003 | 50.89 | reference | — | — | — |
| literal-type | 512 | candidate | 28.887 | 28.331–31.416 | 60.30 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 426.395 | 381.636–538.948 | 52.73 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 38.646 | 37.644–44.439 | 63.31 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 536.101 | 495.599–585.126 | 53.33 | reference | — | — | — |
| literal-type | 1000 | candidate | 55.612 | 49.926–66.446 | 63.81 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.9.0, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
