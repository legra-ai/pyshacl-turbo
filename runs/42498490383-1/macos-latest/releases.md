# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-08T16:59:35.486610+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `74fb5c25dde149710047215b55bc9b3ccafd257d`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 6.935 | 6.634–7.770 | 57.94 | equal | 9.26× | — | — |
| pipeline_rdfs | 100 | python-reference | 64.235 | 61.761–74.711 | 59.23 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 18.645 | 17.351–21.610 | 54.45 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.983 | 15.682–19.601 | 58.38 | equal | 14.59× | — | — |
| pipeline_owlrl | 100 | python-reference | 233.139 | 159.761–259.052 | 59.48 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 35.290 | 30.369–46.742 | 56.77 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 274.762 | 220.078–354.460 | 110.53 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 633.447 | 616.267–1031.116 | 64.75 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 45.532 | 42.831–46.842 | 63.56 | equal | 13.91× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1154.343 | 989.383–1295.919 | 65.78 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 84.774 | 82.302–88.744 | 62.83 | equal | 13.62× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 260.647 | 225.668–312.927 | 115.62 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 19.896 | 19.640–24.068 | 47.33 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.078 | 3.988–4.292 | 55.52 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 23.795 | 23.074–25.457 | 47.06 | reference | — | — | — |
| literal-type | 32 | candidate | 5.092 | 4.699–6.111 | 55.66 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 49.557 | 47.989–54.430 | 47.28 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.414 | 6.340–7.507 | 55.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.066 | 8.456–9.688 | 55.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 61.765 | 60.079–64.050 | 47.42 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.271 | 15.479–23.476 | 58.59 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 170.534 | 165.379–198.942 | 49.00 | reference | — | — | — |
| literal-type | 512 | python-reference | 248.162 | 236.712–282.609 | 49.28 | reference | — | — | — |
| literal-type | 512 | candidate | 21.404 | 21.197–21.775 | 58.72 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 358.661 | 318.117–472.103 | 51.23 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 27.779 | 27.306–28.768 | 61.78 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 425.148 | 411.401–479.318 | 51.78 | reference | — | — | — |
| literal-type | 1000 | candidate | 42.866 | 41.009–54.212 | 62.31 | different | — | logical_inplace_owlrl_different | — |
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
