# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-17T18:37:11.229792+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `7f9683b8e9f9b501579e60cfd956f9386b4fb27d`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 5.550 | 5.338–5.649 | 76.47 | equal | 8.74× | — | — |
| pipeline_rdfs | 100 | python-reference | 48.525 | 48.026–50.011 | 55.70 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 15.423 | 14.693–18.260 | 53.64 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 14.155 | 13.851–14.407 | 77.16 | equal | 8.12× | — | — |
| pipeline_owlrl | 100 | python-reference | 114.950 | 113.650–118.392 | 55.88 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 24.004 | 23.182–28.624 | 53.62 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 159.374 | 147.876–233.785 | 81.88 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 509.739 | 487.809–574.861 | 61.18 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 40.174 | 40.075–41.765 | 80.56 | equal | 12.69× | — | — |
| pipeline_owlrl | 1000 | python-reference | 800.732 | 784.930–887.999 | 62.12 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 89.706 | 88.164–91.249 | 80.98 | equal | 8.93× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 210.363 | 201.095–271.006 | 88.41 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 17.242 | 16.985–17.930 | 51.82 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.224 | 3.155–3.239 | 74.18 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 20.379 | 19.713–21.372 | 85.69 | reference | — | — | — |
| literal-type | 32 | candidate | 3.615 | 3.541–3.635 | 95.19 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 41.356 | 41.244–42.617 | 119.94 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 5.481 | 5.377–5.623 | 119.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 6.805 | 6.785–6.876 | 228.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 52.494 | 51.825–55.384 | 228.09 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 15.193 | 14.332–15.519 | 339.29 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 139.098 | 137.790–168.588 | 339.29 | reference | — | — | — |
| literal-type | 512 | python-reference | 184.773 | 180.597–213.586 | 655.82 | reference | — | — | — |
| literal-type | 512 | candidate | 20.056 | 19.708–20.725 | 655.82 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 263.740 | 261.589–349.291 | 1064.13 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 26.671 | 26.196–27.038 | 1064.13 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 351.725 | 344.098–374.958 | 1659.18 | reference | — | — | — |
| literal-type | 1000 | candidate | 39.132 | 38.786–39.547 | 1659.18 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.2, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
