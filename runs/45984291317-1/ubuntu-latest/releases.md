# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T11:53:16.921671+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `3f319829314500ac13004046836a74c68210dcdb`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.294 | 6.802–9.145 | 77.09 | equal | 6.46× | — | — |
| pipeline_rdfs | 100 | python-reference | 53.611 | 53.454–56.769 | 55.71 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 17.125 | 17.010–21.446 | 54.13 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 22.675 | 19.357–24.330 | 77.84 | equal | 5.50× | — | — |
| pipeline_owlrl | 100 | python-reference | 124.716 | 122.016–127.405 | 55.93 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 27.955 | 26.518–30.196 | 54.15 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 177.059 | 167.427–292.909 | 82.41 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 541.919 | 538.382–650.772 | 61.12 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 52.693 | 50.006–55.382 | 81.26 | equal | 10.28× | — | — |
| pipeline_owlrl | 1000 | python-reference | 855.774 | 853.181–987.290 | 62.22 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 113.417 | 105.427–124.818 | 81.76 | equal | 7.55× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 243.232 | 228.771–347.641 | 88.76 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 18.116 | 17.878–18.324 | 52.23 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.585 | 3.806–10.363 | 74.51 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 21.206 | 21.041–22.002 | 86.11 | reference | — | — | — |
| literal-type | 32 | candidate | 5.615 | 4.092–7.277 | 95.61 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 52.157 | 48.920–56.438 | 120.48 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.816 | 6.043–8.582 | 120.48 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.668 | 8.336–12.133 | 228.95 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 54.820 | 54.556–55.422 | 228.95 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.490 | 16.883–26.756 | 340.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 150.849 | 149.847–202.608 | 340.08 | reference | — | — | — |
| literal-type | 512 | python-reference | 194.384 | 191.726–244.320 | 656.25 | reference | — | — | — |
| literal-type | 512 | candidate | 24.977 | 21.814–29.833 | 656.25 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 281.693 | 274.948–370.894 | 1064.56 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 36.800 | 32.376–41.814 | 1064.56 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 380.538 | 373.025–400.095 | 1660.15 | reference | — | — | — |
| literal-type | 1000 | candidate | 47.803 | 43.382–64.865 | 1660.15 | different | — | logical_inplace_owlrl_different | — |
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
