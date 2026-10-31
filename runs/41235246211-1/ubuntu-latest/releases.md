# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T19:56:55.765885+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `d8a3c162ae4518949f8e3fdb6ae515a515722696`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 14.364 | 13.698–14.500 | 64.55 | equal | 9.13× | — | — |
| pipeline_rdfs | 100 | python-reference | 131.159 | 130.274–132.465 | 47.36 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 34.313 | 33.815–39.722 | 44.29 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.967 | 23.560–24.036 | 65.72 | equal | 13.21× | — | — |
| pipeline_owlrl | 100 | python-reference | 316.548 | 315.282–323.133 | 47.57 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 51.609 | 50.687–56.695 | 45.45 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 343.660 | 332.996–457.244 | 73.91 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1303.064 | 1286.731–1397.269 | 52.89 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 110.217 | 106.095–113.763 | 70.07 | equal | 11.82× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2173.055 | 2162.142–2303.583 | 53.79 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 142.682 | 139.844–270.242 | 69.63 | equal | 15.23× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 458.466 | 439.479–540.731 | 80.43 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 47.687 | 47.311–49.487 | 42.83 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.781 | 5.653–5.916 | 63.53 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 54.574 | 54.297–55.345 | 76.58 | reference | — | — | — |
| literal-type | 32 | candidate | 6.326 | 6.255–6.577 | 86.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 115.685 | 115.432–117.267 | 110.83 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.593 | 9.364–9.861 | 110.83 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.493 | 11.382–11.758 | 218.93 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 143.824 | 142.467–145.893 | 218.93 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 24.872 | 23.961–25.412 | 330.26 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 388.124 | 385.088–428.218 | 330.26 | reference | — | — | — |
| literal-type | 512 | python-reference | 514.759 | 511.152–557.119 | 646.67 | reference | — | — | — |
| literal-type | 512 | candidate | 32.904 | 32.119–33.280 | 646.67 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 745.289 | 734.794–856.402 | 1055.02 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 44.110 | 43.641–47.496 | 1055.02 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 960.592 | 949.783–967.690 | 1650.13 | reference | — | — | — |
| literal-type | 1000 | candidate | 59.490 | 59.284–60.477 | 1650.13 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.1, rdflib-turbo 0.2.0a23

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
