# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T00:48:47.907102+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `1b741cc9a6cf11bbf9728db421f0e3596bbd4c2a`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 5.943 | 5.788–7.549 | 58.06 | equal | 9.12× | — | — |
| pipeline_rdfs | 100 | python-reference | 54.177 | 53.213–67.691 | 59.30 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 19.480 | 17.033–25.041 | 54.36 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 13.778 | 13.593–15.393 | 58.61 | equal | 9.49× | — | — |
| pipeline_owlrl | 100 | python-reference | 130.748 | 127.777–152.895 | 59.64 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 26.913 | 26.115–28.599 | 56.58 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 167.472 | 158.067–218.096 | 106.64 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 610.001 | 568.558–710.633 | 64.83 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 50.499 | 41.374–57.364 | 63.72 | equal | 12.08× | — | — |
| pipeline_owlrl | 1000 | python-reference | 890.682 | 885.430–950.165 | 65.92 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 78.884 | 78.231–79.945 | 63.03 | equal | 11.29× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 271.938 | 220.619–312.856 | 115.81 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 19.337 | 18.993–20.617 | 47.61 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.565 | 3.532–3.616 | 55.81 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.165 | 22.045–23.952 | 47.66 | reference | — | — | — |
| literal-type | 32 | candidate | 4.020 | 3.970–4.133 | 55.83 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 46.977 | 46.393–47.836 | 47.67 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 5.921 | 5.846–6.257 | 56.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.145 | 7.090–10.534 | 56.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 77.639 | 58.984–88.718 | 47.64 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 14.873 | 14.383–16.430 | 58.75 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 157.849 | 157.145–177.595 | 49.28 | reference | — | — | — |
| literal-type | 512 | python-reference | 225.516 | 206.013–239.346 | 49.55 | reference | — | — | — |
| literal-type | 512 | candidate | 19.314 | 19.032–19.356 | 58.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 302.104 | 296.718–367.563 | 51.48 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 25.167 | 24.866–27.598 | 62.00 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 393.490 | 387.549–449.932 | 52.11 | reference | — | — | — |
| literal-type | 1000 | candidate | 34.699 | 34.190–35.636 | 62.55 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.7, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
