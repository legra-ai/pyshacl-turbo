# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T13:21:53.192418+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `5be2fd5b65a8200bb299b744f781034fa902baff`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.143 | 8.920–9.398 | 76.61 | equal | 10.38× | — | — |
| pipeline_rdfs | 100 | python-reference | 94.916 | 93.985–98.648 | 55.65 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.288 | 26.846–31.537 | 54.16 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 19.911 | 19.663–20.241 | 77.35 | equal | 11.22× | — | — |
| pipeline_owlrl | 100 | python-reference | 223.506 | 222.125–226.047 | 55.92 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 42.009 | 41.121–45.155 | 54.13 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 271.294 | 264.203–356.741 | 82.46 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1007.798 | 997.199–1089.751 | 61.17 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 65.804 | 64.442–67.429 | 80.79 | equal | 15.32× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1523.987 | 1518.273–1625.330 | 62.07 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 124.042 | 123.082–125.148 | 81.27 | equal | 12.29× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 359.568 | 353.035–429.396 | 88.86 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.694 | 32.342–34.662 | 52.34 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.833 | 4.785–4.991 | 74.50 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 38.328 | 37.999–38.542 | 86.22 | reference | — | — | — |
| literal-type | 32 | candidate | 5.398 | 5.380–5.441 | 95.72 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 80.327 | 79.825–80.592 | 120.59 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.054 | 7.951–8.219 | 120.59 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.077 | 9.954–10.513 | 228.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 102.018 | 101.448–102.566 | 228.97 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.160 | 20.774–21.465 | 340.28 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 270.287 | 268.034–297.769 | 340.28 | reference | — | — | — |
| literal-type | 512 | python-reference | 351.442 | 348.267–380.830 | 656.45 | reference | — | — | — |
| literal-type | 512 | candidate | 29.030 | 28.487–29.582 | 656.45 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 510.468 | 505.607–581.110 | 1064.72 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 38.040 | 37.463–38.609 | 1064.72 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 672.385 | 666.576–676.648 | 1660.20 | reference | — | — | — |
| literal-type | 1000 | candidate | 52.317 | 51.835–53.120 | 1660.20 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.11, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
