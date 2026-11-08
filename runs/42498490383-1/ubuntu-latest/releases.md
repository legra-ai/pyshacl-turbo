# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-08T16:53:56.150960+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `74fb5c25dde149710047215b55bc9b3ccafd257d`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.972 | 8.654–12.682 | 75.85 | equal | 10.61× | — | — |
| pipeline_rdfs | 100 | python-reference | 95.216 | 94.896–98.108 | 55.60 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 28.297 | 27.375–33.721 | 54.04 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.736 | 20.343–21.010 | 77.42 | equal | 10.67× | — | — |
| pipeline_owlrl | 100 | python-reference | 221.207 | 220.098–224.039 | 55.92 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 43.268 | 41.864–46.393 | 54.09 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 272.957 | 265.286–355.389 | 82.38 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1013.259 | 998.056–1088.873 | 61.16 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 65.018 | 64.266–66.784 | 79.97 | equal | 15.58× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1506.068 | 1493.324–1597.020 | 62.16 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 124.461 | 123.971–125.438 | 81.55 | equal | 12.10× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 364.871 | 358.575–425.939 | 88.90 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.271 | 31.994–32.512 | 51.90 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.883 | 4.818–4.923 | 73.96 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 37.712 | 37.374–38.236 | 85.77 | reference | — | — | — |
| literal-type | 32 | candidate | 5.524 | 5.367–5.808 | 95.27 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 79.949 | 79.362–80.431 | 120.02 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.092 | 7.957–8.214 | 120.02 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.332 | 10.116–10.742 | 228.15 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 99.283 | 98.180–100.187 | 228.15 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.153 | 20.943–21.378 | 339.46 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 270.330 | 269.283–300.071 | 339.46 | reference | — | — | — |
| literal-type | 512 | python-reference | 349.634 | 346.188–379.656 | 655.84 | reference | — | — | — |
| literal-type | 512 | candidate | 29.142 | 28.719–29.398 | 655.84 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 510.970 | 505.222–599.616 | 1064.25 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 38.300 | 37.933–39.291 | 1064.25 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 674.114 | 666.704–687.688 | 1659.32 | reference | — | — | — |
| literal-type | 1000 | candidate | 53.285 | 52.731–54.641 | 1659.32 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.10.1, rdflib-turbo 0.2.0a37

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
