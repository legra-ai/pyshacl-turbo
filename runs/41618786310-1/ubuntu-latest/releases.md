# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-03T10:40:13.423219+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `8681c940fb816f864f3b2452fa760faed78e574c`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.293 | 10.072–10.565 | 66.16 | equal | 13.37× | — | — |
| pipeline_rdfs | 100 | python-reference | 137.617 | 132.423–142.411 | 47.27 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 34.340 | 33.994–39.633 | 44.85 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.683 | 23.366–23.911 | 66.68 | equal | 14.21× | — | — |
| pipeline_owlrl | 100 | python-reference | 336.461 | 334.156–344.293 | 47.65 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 51.357 | 50.253–56.430 | 45.94 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 349.541 | 341.141–464.147 | 74.66 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1340.935 | 1330.625–1394.872 | 52.88 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 68.489 | 68.369–71.610 | 71.23 | equal | 19.58× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2263.352 | 2237.220–2369.873 | 53.89 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 139.008 | 138.093–195.952 | 70.82 | equal | 16.28× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 428.820 | 423.237–509.544 | 81.29 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 47.445 | 47.068–49.257 | 42.75 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.357 | 5.332–5.643 | 64.88 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 57.168 | 56.715–63.674 | 76.75 | reference | — | — | — |
| literal-type | 32 | candidate | 6.260 | 6.064–6.297 | 86.25 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 114.727 | 114.058–116.174 | 110.88 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.328 | 9.251–9.421 | 110.88 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.421 | 11.226–14.599 | 219.02 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 149.573 | 148.760–152.022 | 219.02 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 23.986 | 23.787–24.611 | 330.23 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 409.674 | 401.410–432.480 | 330.23 | reference | — | — | — |
| literal-type | 512 | python-reference | 510.453 | 505.473–550.544 | 646.77 | reference | — | — | — |
| literal-type | 512 | candidate | 33.202 | 32.697–34.025 | 646.77 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 747.558 | 732.734–828.568 | 1055.12 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 44.715 | 42.862–47.003 | 1055.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 959.014 | 938.472–971.685 | 1650.21 | reference | — | — | — |
| literal-type | 1000 | candidate | 59.999 | 59.468–60.558 | 1650.21 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.9.0, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
