# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T10:58:31.418588+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `3f319829314500ac13004046836a74c68210dcdb`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.286 | 9.021–13.769 | 76.58 | equal | 9.38× | — | — |
| pipeline_rdfs | 100 | python-reference | 87.144 | 86.645–89.516 | 55.64 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.208 | 26.941–32.194 | 54.08 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.590 | 20.369–20.908 | 77.25 | equal | 10.24× | — | — |
| pipeline_owlrl | 100 | python-reference | 210.761 | 209.008–214.988 | 55.90 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 42.193 | 41.587–45.764 | 54.14 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 272.391 | 264.290–369.726 | 82.36 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 907.391 | 902.281–1002.457 | 61.15 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 67.198 | 66.819–70.736 | 80.73 | equal | 13.50× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1446.098 | 1436.533–1549.410 | 62.16 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 128.766 | 127.513–131.004 | 81.26 | equal | 11.23× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 362.875 | 358.165–438.953 | 88.98 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 31.550 | 30.976–33.600 | 52.57 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.059 | 4.935–5.090 | 74.27 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 36.600 | 36.299–38.156 | 86.32 | reference | — | — | — |
| literal-type | 32 | candidate | 5.697 | 5.571–5.734 | 95.82 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 77.251 | 77.097–78.473 | 120.70 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.448 | 8.349–8.524 | 120.70 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.367 | 10.194–10.548 | 229.11 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 94.061 | 93.593–95.760 | 229.11 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.905 | 21.587–22.161 | 340.26 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 266.377 | 263.717–299.838 | 340.26 | reference | — | — | — |
| literal-type | 512 | python-reference | 332.826 | 330.339–367.622 | 656.50 | reference | — | — | — |
| literal-type | 512 | candidate | 29.851 | 29.419–33.612 | 656.50 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 490.622 | 486.750–564.886 | 1064.62 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 39.563 | 39.364–39.847 | 1064.62 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 640.926 | 632.530–651.715 | 1660.12 | reference | — | — | — |
| literal-type | 1000 | candidate | 54.694 | 53.953–59.250 | 1660.12 | different | — | logical_inplace_owlrl_different | — |
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
