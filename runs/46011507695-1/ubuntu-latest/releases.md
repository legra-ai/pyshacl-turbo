# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T14:09:54.166190+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `8adb778f823fb5b77c9c45df2ccdd5b3afc802ab`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 6.485 | 6.138–6.735 | 76.54 | equal | 7.89× | — | — |
| pipeline_rdfs | 100 | python-reference | 51.191 | 50.908–73.744 | 55.72 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 15.238 | 14.885–17.946 | 54.06 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 14.694 | 14.476–27.747 | 77.25 | equal | 8.23× | — | — |
| pipeline_owlrl | 100 | python-reference | 120.877 | 118.952–141.360 | 55.90 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 25.019 | 24.035–28.932 | 54.09 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 169.568 | 162.502–286.144 | 82.48 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 545.246 | 525.685–679.436 | 61.23 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 45.114 | 44.287–47.914 | 80.72 | equal | 12.09× | — | — |
| pipeline_owlrl | 1000 | python-reference | 872.988 | 858.196–1077.198 | 62.21 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 93.476 | 92.310–97.929 | 81.22 | equal | 9.34× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 247.915 | 241.075–360.389 | 88.94 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3384.765 | 3301.440–3625.780 | 400.76 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 13385.868 | 13194.999–14112.315 | 126.22 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 499.902 | 479.746–535.051 | 123.67 | equal | 26.78× | — | — |
| pipeline_owlrl | 10000 | python-reference | 8718.170 | 8497.474–9018.522 | 134.61 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1343.109 | 1315.124–1717.823 | 124.85 | equal | 6.49× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5063.182 | 4554.885–5190.854 | 460.60 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 18.102 | 17.889–18.406 | 169.42 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.485 | 3.375–3.645 | 169.42 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 3.968 | 3.899–4.203 | 202.27 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 20.937 | 20.874–21.107 | 202.27 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.118 | 5.893–6.193 | 240.91 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 44.808 | 43.652–48.257 | 240.91 | reference | — | — | — |
| literal-type | 128 | python-reference | 57.209 | 56.621–58.002 | 329.58 | reference | — | — | — |
| literal-type | 128 | candidate | 7.519 | 7.366–7.606 | 329.58 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 155.852 | 148.671–190.652 | 440.32 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.733 | 16.001–17.361 | 440.32 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 196.197 | 192.684–240.167 | 753.54 | reference | — | — | — |
| literal-type | 512 | candidate | 22.358 | 22.128–22.593 | 753.54 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 28.854 | 28.231–29.405 | 1159.46 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 294.658 | 285.419–397.020 | 1159.46 | reference | — | — | — |
| literal-type | 1000 | candidate | 41.043 | 40.637–41.580 | 1753.58 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 385.777 | 377.315–404.963 | 1753.58 | reference | — | — | — |
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
