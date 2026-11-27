# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T12:58:38.230823+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `8adb778f823fb5b77c9c45df2ccdd5b3afc802ab`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.226 | 7.309–11.669 | 58.05 | equal | 6.92× | — | — |
| pipeline_rdfs | 100 | python-reference | 56.882 | 55.496–60.311 | 59.30 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 18.092 | 17.793–23.528 | 54.81 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.666 | 15.922–24.766 | 58.56 | equal | 8.13× | — | — |
| pipeline_owlrl | 100 | python-reference | 135.567 | 128.174–140.297 | 59.59 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 29.521 | 28.174–33.769 | 57.00 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 190.520 | 186.133–254.140 | 111.14 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 608.366 | 578.486–805.262 | 64.78 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 43.842 | 40.973–47.005 | 63.83 | equal | 13.88× | — | — |
| pipeline_owlrl | 1000 | python-reference | 966.542 | 933.842–1090.549 | 66.00 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 86.008 | 82.217–103.595 | 63.16 | equal | 11.24× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 251.935 | 232.508–297.018 | 120.92 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 20.018 | 19.839–20.958 | 47.64 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.106 | 4.073–4.213 | 55.84 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.839 | 22.455–24.935 | 47.64 | reference | — | — | — |
| literal-type | 32 | candidate | 4.341 | 4.201–4.469 | 55.81 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 50.398 | 49.377–51.808 | 47.61 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.181 | 6.098–8.771 | 56.08 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.538 | 7.487–7.983 | 56.25 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 65.548 | 60.827–78.386 | 47.62 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 20.099 | 17.268–27.328 | 58.75 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 165.101 | 161.931–199.610 | 49.22 | reference | — | — | — |
| literal-type | 512 | python-reference | 242.894 | 218.996–274.947 | 49.55 | reference | — | — | — |
| literal-type | 512 | candidate | 20.323 | 19.198–22.393 | 59.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 366.264 | 330.773–431.410 | 51.48 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 25.514 | 25.293–27.666 | 62.06 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 432.983 | 398.200–506.124 | 51.97 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.168 | 37.102–43.035 | 62.47 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.5, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
