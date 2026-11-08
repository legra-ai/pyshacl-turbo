# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-08T16:27:01.205629+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `74fb5c25dde149710047215b55bc9b3ccafd257d`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.808 | 9.557–15.935 | 75.87 | equal | 9.94× | — | — |
| pipeline_rdfs | 100 | python-reference | 97.513 | 95.700–101.851 | 55.73 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 30.148 | 27.861–33.522 | 54.31 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.692 | 20.125–20.943 | 76.49 | equal | 11.10× | — | — |
| pipeline_owlrl | 100 | python-reference | 229.587 | 225.671–233.898 | 55.88 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 43.384 | 42.845–47.193 | 54.23 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 276.624 | 267.566–360.129 | 82.34 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1026.288 | 1012.663–1122.296 | 61.14 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 67.879 | 66.485–69.875 | 79.99 | equal | 15.12× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1554.541 | 1540.864–1666.216 | 62.21 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 131.696 | 126.546–139.655 | 80.47 | equal | 11.80× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 388.847 | 372.935–467.110 | 89.01 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.293 | 32.110–32.688 | 51.95 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.081 | 4.921–5.195 | 73.90 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 37.296 | 36.779–37.831 | 85.95 | reference | — | — | — |
| literal-type | 32 | candidate | 5.518 | 5.363–5.538 | 95.45 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 81.041 | 80.516–81.586 | 120.08 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.414 | 8.264–8.442 | 120.08 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.600 | 10.224–10.751 | 228.16 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 101.440 | 100.627–103.277 | 228.16 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.909 | 21.427–22.076 | 339.37 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 270.679 | 269.460–306.930 | 339.37 | reference | — | — | — |
| literal-type | 512 | python-reference | 353.354 | 351.714–390.206 | 655.91 | reference | — | — | — |
| literal-type | 512 | candidate | 29.463 | 29.030–29.839 | 655.91 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 514.682 | 503.193–592.264 | 1064.36 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 38.561 | 38.499–45.322 | 1064.36 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 672.473 | 658.941–678.570 | 1659.36 | reference | — | — | — |
| literal-type | 1000 | candidate | 54.303 | 52.909–55.614 | 1659.36 | different | — | logical_inplace_owlrl_different | — |
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
