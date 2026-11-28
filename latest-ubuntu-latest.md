# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T07:53:23.690155+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `803b555b073e68cd471cca1ecdfa05969f88d857`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 6.965 | 6.807–13.159 | 76.66 | equal | 7.79× | — | — |
| pipeline_rdfs | 100 | python-reference | 54.267 | 53.364–58.482 | 55.66 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 19.680 | 18.348–26.132 | 54.20 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.964 | 16.671–17.386 | 77.36 | equal | 7.72× | — | — |
| pipeline_owlrl | 100 | python-reference | 130.965 | 129.733–136.667 | 55.86 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 30.215 | 29.071–36.694 | 54.22 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 209.851 | 205.485–374.725 | 82.43 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 592.389 | 583.044–770.495 | 61.11 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 53.422 | 49.388–56.070 | 80.82 | equal | 11.09× | — | — |
| pipeline_owlrl | 1000 | python-reference | 936.668 | 929.099–1133.822 | 62.20 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 112.104 | 111.293–118.176 | 81.49 | equal | 8.36× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 303.971 | 293.432–441.444 | 88.94 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 18.982 | 18.845–19.313 | 52.40 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.976 | 3.934–4.344 | 74.42 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 21.474 | 21.289–21.641 | 86.28 | reference | — | — | — |
| literal-type | 32 | candidate | 4.320 | 4.298–4.425 | 95.78 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 45.256 | 44.942–49.078 | 120.65 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.561 | 6.380–7.071 | 120.65 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.164 | 8.023–8.385 | 229.00 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 59.045 | 58.150–60.417 | 229.00 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.013 | 16.969–18.268 | 340.15 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 160.033 | 155.561–228.766 | 340.15 | reference | — | — | — |
| literal-type | 512 | python-reference | 203.478 | 201.474–272.745 | 656.34 | reference | — | — | — |
| literal-type | 512 | candidate | 22.616 | 22.437–22.728 | 656.34 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 300.679 | 299.082–438.539 | 1064.64 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 31.322 | 30.090–31.912 | 1064.64 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 399.140 | 394.849–405.983 | 1660.14 | reference | — | — | — |
| literal-type | 1000 | candidate | 44.707 | 43.892–45.845 | 1660.14 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.8, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
