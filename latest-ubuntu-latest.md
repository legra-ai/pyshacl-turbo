# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-18T00:46:52.695980+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `2a83794827c5f5dc048128ea2d5dbfe51fda5f90`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.635 | 9.858–19.719 | 76.44 | equal | 9.72× | — | — |
| pipeline_rdfs | 100 | python-reference | 103.418 | 101.313–106.610 | 55.71 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 30.980 | 29.833–37.921 | 55.07 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.053 | 20.852–23.143 | 77.16 | equal | 9.91× | — | — |
| pipeline_owlrl | 100 | python-reference | 228.412 | 227.846–231.356 | 55.86 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 50.509 | 49.190–58.719 | 55.14 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 334.170 | 315.913–484.224 | 83.41 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1050.572 | 1041.317–1202.550 | 61.15 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 77.837 | 70.518–85.072 | 80.56 | equal | 13.50× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1596.580 | 1573.839–1770.310 | 62.18 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 163.238 | 146.632–169.496 | 81.16 | equal | 9.78× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 456.929 | 452.192–551.070 | 89.89 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 34.098 | 33.848–34.874 | 51.82 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.309 | 5.061–5.572 | 74.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 38.687 | 38.064–40.250 | 85.69 | reference | — | — | — |
| literal-type | 32 | candidate | 6.146 | 5.751–6.268 | 95.19 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 81.378 | 79.981–86.146 | 119.94 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.983 | 8.856–9.886 | 119.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.347 | 10.931–11.764 | 228.30 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 102.720 | 102.196–104.555 | 228.30 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 22.996 | 21.351–25.293 | 339.47 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 278.342 | 274.206–337.530 | 339.47 | reference | — | — | — |
| literal-type | 512 | python-reference | 359.526 | 356.070–428.514 | 656.01 | reference | — | — | — |
| literal-type | 512 | candidate | 29.967 | 29.191–31.622 | 656.01 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 525.959 | 518.640–660.961 | 1064.23 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 43.043 | 40.950–46.069 | 1064.23 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 694.065 | 689.932–708.283 | 1659.24 | reference | — | — | — |
| literal-type | 1000 | candidate | 53.095 | 52.609–54.034 | 1659.24 | different | — | logical_inplace_owlrl_different | — |
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
