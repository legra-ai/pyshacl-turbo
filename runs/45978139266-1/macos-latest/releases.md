# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T10:22:35.828424+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `e44f35858166d02881cd2725dcf9db2d6863d6e4`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.198 | 7.953–12.109 | 58.08 | equal | 10.63× | — | — |
| pipeline_rdfs | 100 | python-reference | 97.743 | 60.942–110.603 | 59.28 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 19.758 | 18.247–27.523 | 54.64 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.317 | 14.893–20.610 | 58.66 | equal | 10.73× | — | — |
| pipeline_owlrl | 100 | python-reference | 185.769 | 156.246–196.283 | 59.67 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 41.623 | 37.436–62.946 | 56.72 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 219.096 | 198.477–397.430 | 109.23 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 746.178 | 674.874–951.760 | 64.97 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 47.802 | 45.296–55.660 | 63.81 | equal | 15.61× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1176.554 | 1053.071–1225.498 | 66.06 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 116.175 | 111.080–140.866 | 63.30 | equal | 10.13× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 414.692 | 325.844–549.068 | 118.75 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 42.480 | 25.567–51.862 | 47.64 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.611 | 4.795–6.072 | 55.88 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 38.554 | 32.922–48.386 | 47.58 | reference | — | — | — |
| literal-type | 32 | candidate | 5.565 | 5.058–9.163 | 55.97 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 86.779 | 72.747–129.809 | 47.61 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.762 | 8.215–12.595 | 56.16 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.974 | 8.490–11.397 | 56.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 95.972 | 80.423–113.508 | 47.62 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.080 | 17.392–41.815 | 58.81 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 218.206 | 181.086–259.008 | 49.25 | reference | — | — | — |
| literal-type | 512 | python-reference | 286.830 | 235.057–382.525 | 49.55 | reference | — | — | — |
| literal-type | 512 | candidate | 21.990 | 20.973–28.353 | 59.11 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 377.499 | 353.809–475.050 | 51.44 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 30.352 | 29.573–32.974 | 62.08 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 512.672 | 461.102–560.637 | 52.06 | reference | — | — | — |
| literal-type | 1000 | candidate | 49.433 | 40.248–55.763 | 62.58 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
