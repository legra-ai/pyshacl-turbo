# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-16T14:50:30.319748+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `8dbe8d3628800f77a0bee164caaaebff43207eaf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.459 | 7.341–7.555 | 76.38 | equal | 9.09× | — | — |
| pipeline_rdfs | 100 | python-reference | 67.833 | 67.348–71.556 | 55.68 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.800 | 21.029–26.312 | 54.15 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.342 | 15.996–16.477 | 77.13 | equal | 9.99× | — | — |
| pipeline_owlrl | 100 | python-reference | 163.320 | 162.899–167.094 | 55.84 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 32.540 | 32.073–35.822 | 54.24 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 215.963 | 207.627–297.057 | 82.54 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 699.263 | 696.333–781.827 | 61.21 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 53.325 | 52.556–56.176 | 80.49 | equal | 13.11× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1121.355 | 1106.665–1248.843 | 62.16 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 102.183 | 101.059–104.260 | 80.91 | equal | 10.97× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 297.420 | 294.245–365.334 | 88.80 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.173 | 23.915–24.493 | 51.94 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.995 | 3.917–4.085 | 74.23 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.747 | 27.387–27.821 | 85.82 | reference | — | — | — |
| literal-type | 32 | candidate | 4.497 | 4.449–4.688 | 95.32 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 59.345 | 58.810–59.715 | 120.07 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.690 | 6.617–6.815 | 120.07 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.179 | 8.059–8.242 | 228.15 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 74.288 | 73.238–74.425 | 228.15 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.315 | 17.179–17.511 | 339.33 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 199.208 | 198.369–233.976 | 339.33 | reference | — | — | — |
| literal-type | 512 | python-reference | 264.574 | 259.960–304.524 | 655.99 | reference | — | — | — |
| literal-type | 512 | candidate | 23.711 | 23.290–23.775 | 655.99 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 382.041 | 380.078–462.056 | 1064.27 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 31.306 | 31.152–32.055 | 1064.27 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 494.177 | 491.142–513.955 | 1659.19 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.241 | 42.851–43.521 | 1659.19 | different | — | logical_inplace_owlrl_different | — |
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
