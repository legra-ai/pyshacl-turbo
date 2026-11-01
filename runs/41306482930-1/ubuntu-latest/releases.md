# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-01T13:20:37.607798+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `9d5910e6b6b2e011859a8b3b8a5b7251cb5d4d5b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 11.511 | 11.477–11.824 | 64.43 | equal | 8.15× | — | — |
| pipeline_rdfs | 100 | python-reference | 93.829 | 93.573–95.776 | 47.38 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 25.395 | 24.741–29.701 | 44.36 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 21.451 | 21.076–21.537 | 65.48 | equal | 10.76× | — | — |
| pipeline_owlrl | 100 | python-reference | 230.875 | 228.121–233.359 | 47.60 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 38.670 | 38.090–42.276 | 45.41 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 255.410 | 249.506–334.123 | 73.89 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 942.820 | 925.562–1009.402 | 52.78 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 90.872 | 89.581–92.196 | 69.88 | equal | 10.38× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1575.141 | 1562.101–1662.351 | 53.86 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 133.896 | 133.395–191.820 | 69.31 | equal | 11.76× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 337.490 | 332.990–403.543 | 80.41 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 34.356 | 33.711–35.864 | 42.84 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.969 | 4.867–5.043 | 63.47 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 39.986 | 39.706–40.831 | 76.72 | reference | — | — | — |
| literal-type | 32 | candidate | 5.631 | 5.524–5.680 | 86.22 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 84.808 | 84.137–86.709 | 110.97 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.500 | 8.394–8.610 | 110.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.583 | 10.470–10.627 | 219.21 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 105.085 | 103.600–105.835 | 219.21 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 22.297 | 22.255–22.526 | 330.38 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 285.334 | 282.776–318.730 | 330.38 | reference | — | — | — |
| literal-type | 512 | python-reference | 368.119 | 365.498–403.099 | 646.92 | reference | — | — | — |
| literal-type | 512 | candidate | 30.190 | 29.901–30.307 | 646.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 538.717 | 527.327–617.356 | 1055.30 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 40.749 | 40.409–41.245 | 1055.30 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 704.596 | 697.682–714.215 | 1650.36 | reference | — | — | — |
| literal-type | 1000 | candidate | 56.402 | 55.607–56.865 | 1650.36 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.5, rdflib-turbo 0.2.0a27

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
