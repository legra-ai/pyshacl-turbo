# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-16T14:14:19.855045+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `8dbe8d3628800f77a0bee164caaaebff43207eaf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.051 | 6.964–9.520 | 57.94 | equal | 8.35× | — | — |
| pipeline_rdfs | 100 | python-reference | 67.215 | 59.639–73.842 | 59.22 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 19.985 | 18.861–23.334 | 54.70 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.643 | 19.060–29.151 | 58.66 | equal | 7.19× | — | — |
| pipeline_owlrl | 100 | python-reference | 169.924 | 153.637–193.422 | 59.52 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 30.260 | 29.276–35.592 | 56.75 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 193.136 | 189.262–272.068 | 110.89 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 693.498 | 622.784–886.249 | 64.83 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 87.060 | 52.503–107.152 | 63.66 | equal | 7.97× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1157.981 | 1024.161–1343.393 | 65.89 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 96.163 | 91.254–113.419 | 63.09 | equal | 12.04× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 312.070 | 284.374–359.783 | 120.03 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 21.760 | 21.368–24.664 | 47.41 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.776 | 4.375–5.433 | 55.80 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 25.844 | 24.982–26.910 | 47.48 | reference | — | — | — |
| literal-type | 32 | candidate | 10.124 | 4.748–11.667 | 55.77 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 55.770 | 53.654–66.025 | 47.44 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.593 | 6.451–7.902 | 56.08 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.689 | 8.232–11.746 | 56.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 69.405 | 64.729–77.196 | 47.42 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.127 | 16.443–26.841 | 58.72 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 181.293 | 176.606–215.463 | 49.05 | reference | — | — | — |
| literal-type | 512 | python-reference | 232.220 | 225.433–265.199 | 49.27 | reference | — | — | — |
| literal-type | 512 | candidate | 22.714 | 21.805–26.185 | 59.11 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 371.620 | 339.478–474.386 | 51.38 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 31.851 | 31.000–36.176 | 62.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 485.389 | 452.253–558.395 | 51.81 | reference | — | — | — |
| literal-type | 1000 | candidate | 39.476 | 38.586–40.797 | 62.55 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.2, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
