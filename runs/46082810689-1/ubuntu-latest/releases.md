# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T23:48:16.762075+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `894649fe91d30496560937ce6899cc355f1541fc`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.167 | 8.965–9.484 | 76.62 | equal | 10.46× | — | — |
| pipeline_rdfs | 100 | python-reference | 95.906 | 95.424–99.008 | 55.64 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.493 | 27.008–31.365 | 54.08 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.468 | 20.158–23.367 | 77.40 | equal | 10.78× | — | — |
| pipeline_owlrl | 100 | python-reference | 220.592 | 219.905–224.497 | 55.92 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 41.630 | 41.108–45.039 | 54.18 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 270.051 | 262.781–356.063 | 82.48 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 994.644 | 988.659–1082.267 | 60.91 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 66.177 | 65.027–67.069 | 80.70 | equal | 15.03× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1510.507 | 1492.684–1601.942 | 62.09 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 124.494 | 123.957–127.342 | 81.34 | equal | 12.13× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 358.828 | 351.037–424.115 | 88.85 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.832 | 32.521–33.018 | 52.42 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.140 | 5.073–5.203 | 74.59 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 38.000 | 37.458–38.409 | 86.30 | reference | — | — | — |
| literal-type | 32 | candidate | 5.707 | 5.581–5.799 | 95.80 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 81.092 | 80.330–82.060 | 120.67 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.404 | 8.168–9.484 | 120.67 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.296 | 10.070–10.357 | 229.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 100.506 | 98.847–101.402 | 229.12 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.367 | 21.084–21.781 | 340.26 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 270.586 | 268.943–297.477 | 340.26 | reference | — | — | — |
| literal-type | 512 | python-reference | 346.570 | 344.257–376.523 | 656.36 | reference | — | — | — |
| literal-type | 512 | candidate | 29.032 | 28.985–29.278 | 656.36 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 512.913 | 506.510–578.936 | 1064.61 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 38.309 | 38.054–38.740 | 1064.61 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 658.332 | 653.672–678.309 | 1660.08 | reference | — | — | — |
| literal-type | 1000 | candidate | 52.784 | 52.289–54.347 | 1660.08 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.6, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
