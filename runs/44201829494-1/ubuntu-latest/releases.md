# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-17T23:58:55.428009+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `2a83794827c5f5dc048128ea2d5dbfe51fda5f90`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.813 | 7.710–8.394 | 76.48 | equal | 9.47× | — | — |
| pipeline_rdfs | 100 | python-reference | 74.001 | 73.111–79.021 | 55.70 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 24.103 | 22.667–27.596 | 54.01 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.379 | 16.894–18.084 | 77.12 | equal | 9.97× | — | — |
| pipeline_owlrl | 100 | python-reference | 173.275 | 170.215–176.750 | 55.96 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 35.920 | 35.332–39.503 | 54.07 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 240.853 | 230.304–331.048 | 82.45 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 767.769 | 747.577–852.852 | 61.22 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 58.275 | 57.142–63.855 | 80.37 | equal | 13.17× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1221.396 | 1199.592–1319.767 | 62.18 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 110.539 | 108.646–112.950 | 81.03 | equal | 11.05× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 322.656 | 311.320–403.317 | 88.83 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 26.386 | 25.829–26.596 | 52.00 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.629 | 4.547–4.848 | 74.18 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 32.998 | 31.267–36.823 | 85.88 | reference | — | — | — |
| literal-type | 32 | candidate | 4.940 | 4.860–5.286 | 95.50 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 64.038 | 63.434–65.110 | 120.25 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.164 | 7.062–7.352 | 120.25 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.892 | 8.663–9.046 | 228.27 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 79.619 | 76.944–83.573 | 228.27 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 18.855 | 18.637–19.467 | 339.47 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 215.712 | 213.949–255.758 | 339.47 | reference | — | — | — |
| literal-type | 512 | python-reference | 282.945 | 277.663–326.346 | 656.01 | reference | — | — | — |
| literal-type | 512 | candidate | 25.780 | 24.648–26.483 | 656.01 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 425.210 | 417.137–539.091 | 1064.37 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 34.984 | 34.110–35.643 | 1064.37 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 549.929 | 520.582–554.165 | 1659.39 | reference | — | — | — |
| literal-type | 1000 | candidate | 46.503 | 45.903–48.204 | 1659.39 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.3, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
