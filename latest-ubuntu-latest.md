# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-16T01:22:28.157589+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `1337b4db1937e99a029118e12bf94503e9410b8b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 5.803 | 5.428–8.095 | 76.43 | equal | 8.69× | — | — |
| pipeline_rdfs | 100 | python-reference | 50.441 | 50.064–55.167 | 55.63 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 16.561 | 15.502–20.516 | 54.19 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.068 | 14.837–15.438 | 77.16 | equal | 7.66× | — | — |
| pipeline_owlrl | 100 | python-reference | 115.432 | 114.928–117.312 | 55.95 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 25.050 | 23.631–27.671 | 54.28 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 177.504 | 162.432–295.364 | 82.53 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 527.358 | 518.019–655.402 | 61.21 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 43.871 | 41.706–45.317 | 80.55 | equal | 12.02× | — | — |
| pipeline_owlrl | 1000 | python-reference | 844.630 | 816.176–940.068 | 62.18 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 91.948 | 89.681–96.386 | 81.12 | equal | 9.19× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 229.230 | 215.387–302.559 | 88.88 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 17.266 | 17.115–17.398 | 51.78 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.307 | 3.279–3.646 | 74.23 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 20.737 | 20.600–21.088 | 85.65 | reference | — | — | — |
| literal-type | 32 | candidate | 3.621 | 3.565–3.659 | 95.28 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 42.973 | 41.768–45.234 | 119.90 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 5.641 | 5.627–5.911 | 119.90 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 6.893 | 6.865–7.030 | 228.01 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 52.435 | 52.084–53.640 | 228.01 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 14.908 | 14.649–15.437 | 339.21 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 148.818 | 143.742–198.787 | 339.21 | reference | — | — | — |
| literal-type | 512 | python-reference | 189.559 | 185.254–229.843 | 655.74 | reference | — | — | — |
| literal-type | 512 | candidate | 21.403 | 20.177–21.863 | 655.74 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 276.651 | 266.580–372.959 | 1064.18 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 27.066 | 26.714–28.561 | 1064.18 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 383.156 | 380.912–387.462 | 1659.12 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.180 | 36.750–39.865 | 1659.12 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.10.1, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
