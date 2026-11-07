# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-07T11:25:51.939644+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `bc9ec2d32b8345fcaf7a4f0aaac62f273cce658e`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.607 | 9.207–10.535 | 68.83 | equal | 13.55× | — | — |
| pipeline_rdfs | 100 | python-reference | 130.131 | 129.239–148.751 | 48.56 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 32.451 | 32.067–41.096 | 47.72 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 21.979 | 21.745–22.471 | 69.52 | equal | 14.12× | — | — |
| pipeline_owlrl | 100 | python-reference | 310.358 | 309.343–311.760 | 48.89 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 48.356 | 47.718–51.579 | 47.73 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 320.361 | 310.956–404.427 | 76.23 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1281.530 | 1261.666–1361.671 | 53.30 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 67.142 | 66.271–69.827 | 71.99 | equal | 19.09× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2153.901 | 2138.365–2251.900 | 54.81 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 138.940 | 137.983–141.458 | 72.39 | equal | 15.50× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 418.616 | 409.030–489.921 | 82.48 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 4295.082 | 4194.310–4409.742 | 394.42 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 27853.680 | 27768.537–28125.791 | 119.36 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 801.454 | 746.901–832.693 | 116.11 | equal | 34.75× | — | — |
| pipeline_owlrl | 10000 | python-reference | 21185.747 | 21011.421–21408.510 | 127.88 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1646.828 | 1610.794–2158.486 | 116.88 | equal | 12.86× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 6206.488 | 6085.871–6354.780 | 453.14 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 47.827 | 47.540–48.301 | 153.94 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.339 | 5.286–5.448 | 153.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 6.036 | 5.794–6.057 | 186.69 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 55.332 | 54.924–55.750 | 186.69 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.065 | 8.888–9.106 | 225.45 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 116.604 | 115.478–117.625 | 225.45 | reference | — | — | — |
| literal-type | 128 | python-reference | 142.749 | 142.443–143.428 | 314.09 | reference | — | — | — |
| literal-type | 128 | candidate | 11.305 | 11.075–11.483 | 314.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 394.888 | 392.205–431.412 | 424.84 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 23.768 | 23.542–24.051 | 424.84 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 515.557 | 513.879–556.972 | 742.66 | reference | — | — | — |
| literal-type | 512 | candidate | 32.169 | 31.965–32.741 | 742.66 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 43.149 | 42.505–44.113 | 1151.20 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 748.209 | 745.150–848.567 | 1151.20 | reference | — | — | — |
| literal-type | 1000 | candidate | 60.036 | 59.194–62.209 | 1749.82 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 963.695 | 958.444–966.566 | 1749.82 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.10.0, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
