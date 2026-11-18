# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-18T00:52:22.571851+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `2a83794827c5f5dc048128ea2d5dbfe51fda5f90`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.481 | 7.505–10.057 | 58.05 | equal | 10.22× | — | — |
| pipeline_rdfs | 100 | python-reference | 86.693 | 75.678–111.770 | 59.31 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 19.612 | 18.504–24.450 | 54.50 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.796 | 16.385–18.632 | 58.61 | equal | 9.34× | — | — |
| pipeline_owlrl | 100 | python-reference | 166.251 | 142.500–220.547 | 59.45 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 36.180 | 32.965–37.404 | 56.91 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 215.951 | 194.981–285.513 | 110.02 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 749.428 | 629.874–1055.804 | 64.66 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 64.387 | 45.414–102.878 | 63.89 | equal | 11.64× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1203.136 | 1163.373–1574.722 | 65.84 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 109.654 | 91.443–129.574 | 63.17 | equal | 10.97× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 323.391 | 305.286–387.894 | 116.45 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.303 | 23.351–29.611 | 47.64 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.074 | 4.706–6.054 | 55.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 26.630 | 24.175–40.058 | 47.67 | reference | — | — | — |
| literal-type | 32 | candidate | 6.916 | 5.532–9.499 | 55.97 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 61.116 | 52.328–76.983 | 47.47 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.716 | 7.592–13.839 | 56.16 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.293 | 8.227–11.335 | 56.27 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 79.660 | 71.960–110.792 | 47.53 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.049 | 16.616–23.477 | 58.80 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 187.027 | 178.092–264.322 | 49.25 | reference | — | — | — |
| literal-type | 512 | python-reference | 277.848 | 252.501–413.982 | 49.53 | reference | — | — | — |
| literal-type | 512 | candidate | 25.399 | 24.024–28.562 | 59.11 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 524.488 | 388.361–655.760 | 51.39 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 29.985 | 27.939–39.981 | 62.03 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 517.695 | 472.882–651.935 | 52.06 | reference | — | — | — |
| literal-type | 1000 | candidate | 45.890 | 42.125–50.333 | 62.62 | different | — | logical_inplace_owlrl_different | — |
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
