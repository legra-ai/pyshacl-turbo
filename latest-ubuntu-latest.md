# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-03T18:20:00.314230+00:00; platform: Linux-7.0.0-1014-aws-x86_64-with-glibc2.39.
Harness revision: `8f03cd4296b36764950306219408eefd65624b28`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.948 | 7.686–8.582 | 65.98 | equal | 10.31× | — | — |
| pipeline_rdfs | 100 | python-reference | 81.930 | 81.121–82.237 | 47.22 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 22.931 | 22.783–27.871 | 44.18 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.094 | 19.502–20.592 | 66.72 | equal | 9.98× | — | — |
| pipeline_owlrl | 100 | python-reference | 200.503 | 199.201–202.462 | 47.44 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.916 | 34.594–38.092 | 45.20 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 232.949 | 230.046–324.516 | 73.72 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 831.640 | 822.139–903.457 | 52.61 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 54.782 | 53.604–55.918 | 71.06 | equal | 15.18× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1382.698 | 1361.960–1497.424 | 53.77 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 121.245 | 119.853–219.474 | 70.57 | equal | 11.40× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 315.342 | 308.671–397.307 | 79.98 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 30.168 | 29.932–31.867 | 42.76 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.507 | 4.422–4.613 | 64.68 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 34.600 | 34.270–34.801 | 76.51 | reference | — | — | — |
| literal-type | 32 | candidate | 5.116 | 4.967–5.516 | 86.01 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 73.432 | 72.394–74.729 | 110.76 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.056 | 7.754–8.301 | 110.76 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.650 | 9.499–9.907 | 222.89 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 90.466 | 89.267–91.887 | 222.89 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 20.315 | 19.850–20.619 | 334.17 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 245.890 | 243.622–285.153 | 334.17 | reference | — | — | — |
| literal-type | 512 | python-reference | 316.358 | 315.101–360.942 | 648.46 | reference | — | — | — |
| literal-type | 512 | candidate | 26.945 | 26.710–27.357 | 648.46 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 463.835 | 459.793–566.001 | 1055.10 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 37.441 | 36.799–37.977 | 1055.10 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 614.372 | 605.735–622.397 | 1648.72 | reference | — | — | — |
| literal-type | 1000 | candidate | 51.182 | 50.655–51.571 | 1648.72 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.9.1, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
