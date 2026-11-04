# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-04T12:33:22.115060+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `b36b227b1766aee5397e3ff30b3076741e5fefdf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.111 | 9.882–10.423 | 66.28 | equal | 12.87× | — | — |
| pipeline_rdfs | 100 | python-reference | 130.161 | 129.399–131.884 | 47.43 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 33.854 | 33.685–39.475 | 44.27 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.718 | 23.567–23.839 | 66.84 | equal | 13.29× | — | — |
| pipeline_owlrl | 100 | python-reference | 315.316 | 311.427–317.316 | 47.65 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 50.921 | 50.078–55.324 | 45.51 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 336.876 | 328.249–441.391 | 73.98 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1312.653 | 1305.238–1399.084 | 52.79 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 68.320 | 67.765–70.019 | 71.14 | equal | 19.21× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2155.730 | 2143.911–2281.386 | 53.96 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 139.602 | 139.161–244.494 | 70.77 | equal | 15.44× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 429.023 | 419.404–497.957 | 80.40 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 4564.713 | 4410.312–4819.652 | 392.35 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 28170.801 | 28065.970–28554.718 | 118.57 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 865.262 | 822.484–876.290 | 114.04 | equal | 32.56× | — | — |
| pipeline_owlrl | 10000 | python-reference | 21041.919 | 20963.147–21134.808 | 126.50 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1715.917 | 1697.103–2217.215 | 104.91 | equal | 12.26× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 6425.878 | 6248.491–6619.060 | 449.91 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 47.467 | 47.236–49.446 | 152.54 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.589 | 5.504–5.680 | 152.54 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 6.213 | 6.170–6.583 | 185.48 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 55.247 | 54.770–61.912 | 185.48 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.354 | 9.211–9.475 | 224.17 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 116.478 | 115.458–116.635 | 224.17 | reference | — | — | — |
| literal-type | 128 | python-reference | 144.805 | 143.897–146.691 | 312.75 | reference | — | — | — |
| literal-type | 128 | candidate | 11.506 | 11.441–11.600 | 312.75 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 389.940 | 384.853–434.278 | 439.77 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 24.513 | 24.129–24.799 | 439.77 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 505.811 | 499.853–544.637 | 751.86 | reference | — | — | — |
| literal-type | 512 | candidate | 33.070 | 32.590–33.310 | 751.86 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 44.880 | 44.488–58.661 | 1151.61 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 735.371 | 725.387–833.586 | 1151.61 | reference | — | — | — |
| literal-type | 1000 | candidate | 61.096 | 60.341–62.615 | 1748.96 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 966.302 | 964.952–970.819 | 1748.96 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.10.0, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
