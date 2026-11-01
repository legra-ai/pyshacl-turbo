# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-01T11:19:14.425509+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `e5164a97129fa57013b0359b374bebecd333368b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 13.652 | 13.335–14.044 | 64.43 | equal | 8.40× | — | — |
| pipeline_rdfs | 100 | python-reference | 114.659 | 114.581–115.982 | 47.39 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 31.299 | 31.207–37.247 | 44.12 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 24.121 | 24.095–26.570 | 65.39 | equal | 11.33× | — | — |
| pipeline_owlrl | 100 | python-reference | 273.239 | 270.278–279.346 | 47.63 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 45.949 | 45.464–50.339 | 45.42 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 315.612 | 309.648–410.964 | 73.78 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1159.154 | 1152.282–1247.484 | 52.86 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 113.245 | 107.422–119.946 | 70.10 | equal | 10.24× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1925.977 | 1894.668–2027.017 | 53.77 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 159.059 | 154.549–225.451 | 69.48 | equal | 12.11× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 424.532 | 418.274–506.149 | 80.28 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 42.169 | 41.721–43.697 | 42.81 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.508 | 5.419–5.925 | 63.36 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 47.063 | 46.785–48.054 | 76.81 | reference | — | — | — |
| literal-type | 32 | candidate | 6.212 | 6.157–6.421 | 86.31 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 100.527 | 99.954–102.526 | 111.06 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.633 | 9.444–10.891 | 111.06 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.782 | 11.505–12.293 | 219.13 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 126.548 | 126.349–127.699 | 219.13 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 26.692 | 25.348–27.121 | 330.45 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 351.286 | 344.344–393.839 | 330.45 | reference | — | — | — |
| literal-type | 512 | python-reference | 447.515 | 442.019–493.008 | 646.82 | reference | — | — | — |
| literal-type | 512 | candidate | 34.650 | 34.303–35.788 | 646.82 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 650.352 | 647.699–747.036 | 1055.12 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 47.785 | 47.367–48.167 | 1055.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 845.430 | 834.250–859.226 | 1650.22 | reference | — | — | — |
| literal-type | 1000 | candidate | 66.377 | 64.315–68.380 | 1650.22 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.4, rdflib-turbo 0.2.0a24

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
