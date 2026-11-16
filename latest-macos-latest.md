# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-16T01:27:51.856269+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `1337b4db1937e99a029118e12bf94503e9410b8b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.626 | 7.018–12.070 | 58.00 | equal | 7.57× | — | — |
| pipeline_rdfs | 100 | python-reference | 65.291 | 60.100–72.764 | 59.19 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.594 | 19.653–23.930 | 54.80 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.765 | 14.887–26.460 | 58.58 | equal | 8.99× | — | — |
| pipeline_owlrl | 100 | python-reference | 168.759 | 149.871–206.522 | 59.59 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 31.502 | 27.461–33.806 | 57.02 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 219.341 | 171.548–254.485 | 110.55 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 738.452 | 693.761–882.472 | 64.73 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 48.480 | 43.865–57.598 | 63.69 | equal | 15.23× | — | — |
| pipeline_owlrl | 1000 | python-reference | 985.837 | 921.987–1234.503 | 65.91 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 102.105 | 84.980–108.508 | 63.19 | equal | 9.66× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 302.606 | 227.626–446.079 | 120.33 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 19.848 | 19.550–20.163 | 47.59 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.166 | 3.889–4.431 | 55.78 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.050 | 24.588–55.495 | 47.53 | reference | — | — | — |
| literal-type | 32 | candidate | 5.015 | 4.835–5.836 | 55.83 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 58.938 | 47.727–66.496 | 47.61 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.565 | 7.276–9.118 | 56.08 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.194 | 7.107–11.036 | 56.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 59.270 | 58.563–65.811 | 47.50 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 14.876 | 14.428–16.936 | 58.70 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 189.379 | 180.942–218.384 | 49.23 | reference | — | — | — |
| literal-type | 512 | python-reference | 232.290 | 204.699–257.250 | 49.53 | reference | — | — | — |
| literal-type | 512 | candidate | 19.589 | 19.317–23.879 | 59.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 354.963 | 325.800–417.198 | 51.47 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 31.667 | 28.331–33.317 | 62.00 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 441.568 | 402.246–509.452 | 51.94 | reference | — | — | — |
| literal-type | 1000 | candidate | 35.714 | 34.416–41.152 | 62.62 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.10.1, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
