# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T07:18:16.511771+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `5387c5dc1a4e5ee5a2e5c45778a19e4ffa04b83d`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 14.636 | 11.102–17.620 | 59.16 | equal | 4.02× | — | — |
| pipeline_rdfs | 100 | python-reference | 58.859 | 57.226–72.739 | 60.88 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 18.444 | 18.236–26.794 | 55.92 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 21.282 | 16.850–21.950 | 59.67 | equal | 7.25× | — | — |
| pipeline_owlrl | 100 | python-reference | 154.290 | 143.424–165.089 | 61.05 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.370 | 31.954–39.013 | 58.22 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 185.740 | 177.887–251.302 | 111.53 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 619.763 | 599.714–901.194 | 66.27 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 70.754 | 69.204–74.100 | 65.83 | equal | 8.76× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1005.023 | 979.349–1401.819 | 67.39 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 98.416 | 96.414–140.492 | 64.05 | equal | 10.21× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 256.867 | 243.678–313.457 | 121.16 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.555 | 22.186–26.098 | 49.23 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.234 | 4.113–4.299 | 56.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 24.311 | 23.828–24.474 | 49.19 | reference | — | — | — |
| literal-type | 32 | candidate | 4.748 | 4.614–5.126 | 56.98 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 51.179 | 50.822–52.693 | 49.19 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.197 | 6.999–7.413 | 57.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.582 | 8.533–8.735 | 57.38 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 75.868 | 62.531–81.821 | 49.20 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.992 | 17.484–18.101 | 59.84 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 170.396 | 167.470–202.792 | 50.81 | reference | — | — | — |
| literal-type | 512 | python-reference | 251.256 | 223.013–268.358 | 50.88 | reference | — | — | — |
| literal-type | 512 | candidate | 23.786 | 23.588–24.724 | 60.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 383.092 | 328.998–398.567 | 53.03 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 31.151 | 30.581–38.797 | 63.03 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 431.983 | 424.649–498.524 | 53.59 | reference | — | — | — |
| literal-type | 1000 | candidate | 46.099 | 41.784–60.166 | 63.56 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.0, rdflib-turbo 0.2.0a20

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
