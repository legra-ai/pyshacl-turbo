# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-18T12:21:37.561394+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `c5c828aa2d37e30f85d97d54815454e8e0baee66`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 6.318 | 6.154–6.856 | 76.43 | equal | 8.26× | — | — |
| pipeline_rdfs | 100 | python-reference | 52.172 | 51.564–54.992 | 55.65 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 16.990 | 16.821–21.572 | 54.21 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.663 | 15.210–15.890 | 77.06 | equal | 7.96× | — | — |
| pipeline_owlrl | 100 | python-reference | 124.640 | 123.242–130.015 | 56.00 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 26.855 | 25.326–28.813 | 54.23 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 174.416 | 167.336–293.912 | 82.39 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 562.249 | 550.450–668.910 | 61.16 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 45.010 | 43.858–46.455 | 80.45 | equal | 12.49× | — | — |
| pipeline_owlrl | 1000 | python-reference | 882.994 | 865.571–980.779 | 62.16 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 94.495 | 94.041–96.356 | 81.16 | equal | 9.34× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 245.033 | 235.906–344.806 | 88.94 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 18.319 | 18.005–19.479 | 52.46 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.639 | 3.512–3.924 | 74.18 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 20.840 | 20.677–21.135 | 86.33 | reference | — | — | — |
| literal-type | 32 | candidate | 3.728 | 3.653–3.853 | 95.96 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 44.037 | 43.590–44.704 | 120.71 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 5.977 | 5.858–6.627 | 120.71 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.697 | 7.429–7.746 | 228.76 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 56.461 | 55.984–57.290 | 228.76 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 15.619 | 15.484–16.358 | 339.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 149.520 | 146.885–200.664 | 339.92 | reference | — | — | — |
| literal-type | 512 | python-reference | 194.908 | 190.527–249.914 | 656.51 | reference | — | — | — |
| literal-type | 512 | candidate | 21.705 | 21.220–21.897 | 656.51 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 290.562 | 285.564–389.839 | 1064.65 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 27.592 | 26.691–27.996 | 1064.65 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 379.862 | 374.283–419.790 | 1659.70 | reference | — | — | — |
| literal-type | 1000 | candidate | 39.350 | 38.869–56.519 | 1659.70 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
