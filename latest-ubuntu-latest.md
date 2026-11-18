# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-18T11:54:30.039588+00:00; platform: Linux-7.0.0-1016-aws-x86_64-with-glibc2.43.
Harness revision: `c5c828aa2d37e30f85d97d54815454e8e0baee66`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.453 | 6.979–11.697 | 76.96 | equal | 9.64× | — | — |
| pipeline_rdfs | 100 | python-reference | 71.810 | 71.224–76.259 | 55.69 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.091 | 20.815–25.193 | 54.12 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.782 | 16.587–17.189 | 77.66 | equal | 9.83× | — | — |
| pipeline_owlrl | 100 | python-reference | 165.026 | 164.244–170.722 | 56.12 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 32.096 | 31.634–35.090 | 54.31 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 213.880 | 210.538–290.941 | 82.40 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 731.004 | 725.817–792.467 | 61.23 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 51.644 | 50.756–52.537 | 81.09 | equal | 14.15× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1156.333 | 1141.001–1231.884 | 62.37 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 107.315 | 106.347–108.585 | 81.67 | equal | 10.78× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 285.439 | 281.230–354.662 | 88.96 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.063 | 23.332–24.316 | 52.49 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.071 | 4.022–4.163 | 74.73 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.994 | 27.872–28.335 | 86.36 | reference | — | — | — |
| literal-type | 32 | candidate | 4.472 | 4.404–4.585 | 95.86 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 61.679 | 60.726–63.450 | 120.74 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.699 | 6.529–6.776 | 120.74 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.200 | 8.096–8.373 | 228.91 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 74.651 | 73.665–74.941 | 228.91 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.291 | 17.127–18.005 | 340.10 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 201.262 | 200.162–226.433 | 340.10 | reference | — | — | — |
| literal-type | 512 | python-reference | 265.360 | 261.536–292.232 | 656.59 | reference | — | — | — |
| literal-type | 512 | candidate | 23.200 | 22.891–23.427 | 656.59 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 383.594 | 377.619–449.905 | 1064.84 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 31.994 | 31.425–32.458 | 1064.84 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 498.207 | 491.603–501.480 | 1660.00 | reference | — | — | — |
| literal-type | 1000 | candidate | 44.298 | 44.037–45.005 | 1660.00 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
