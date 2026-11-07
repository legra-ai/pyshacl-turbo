# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-07T22:40:00.247597+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `ae8e55f7ecd688d7a1fafa4a73e42c8aab2fba43`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.046 | 6.761–9.794 | 59.42 | equal | 10.96× | — | — |
| pipeline_rdfs | 100 | python-reference | 77.224 | 69.020–89.940 | 60.77 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 29.645 | 27.280–51.721 | 55.98 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.467 | 19.007–28.220 | 59.92 | equal | 8.45× | — | — |
| pipeline_owlrl | 100 | python-reference | 172.852 | 163.937–178.330 | 61.19 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 39.127 | 36.246–48.555 | 58.19 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 185.201 | 171.110–288.841 | 111.03 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 642.024 | 582.815–750.304 | 66.27 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 44.494 | 43.129–55.493 | 65.25 | equal | 14.43× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1019.266 | 986.479–1135.808 | 67.39 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 98.593 | 91.005–118.214 | 64.59 | equal | 10.34× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 252.309 | 227.911–288.455 | 121.56 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 22.140 | 19.366–30.182 | 49.08 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.275 | 4.215–4.408 | 57.11 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.810 | 22.381–24.511 | 49.25 | reference | — | — | — |
| literal-type | 32 | candidate | 4.890 | 4.768–5.080 | 57.33 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 52.594 | 49.338–59.984 | 49.16 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.780 | 6.651–6.872 | 57.36 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.951 | 8.729–9.690 | 57.45 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 63.676 | 62.760–64.040 | 49.20 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 18.094 | 18.005–18.686 | 60.02 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 172.495 | 164.755–215.574 | 50.80 | reference | — | — | — |
| literal-type | 512 | python-reference | 223.900 | 209.831–265.894 | 51.05 | reference | — | — | — |
| literal-type | 512 | candidate | 26.622 | 23.982–27.483 | 60.39 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 323.664 | 304.779–396.556 | 52.91 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 33.070 | 31.712–35.344 | 63.28 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 425.708 | 412.056–430.581 | 53.62 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.230 | 41.532–46.368 | 63.92 | different | — | logical_inplace_owlrl_different | — |
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
