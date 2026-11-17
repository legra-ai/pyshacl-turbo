# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-17T14:03:10.474041+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `e1fb11c010847556649f363b914b1421b7cb59ae`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.200 | 7.934–12.525 | 58.08 | equal | 8.40× | — | — |
| pipeline_rdfs | 100 | python-reference | 77.309 | 69.290–86.361 | 59.30 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 29.782 | 25.078–33.282 | 54.47 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.469 | 18.005–21.102 | 58.66 | equal | 12.24× | — | — |
| pipeline_owlrl | 100 | python-reference | 226.088 | 188.282–233.434 | 59.70 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 60.994 | 52.726–66.623 | 56.64 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 325.447 | 270.414–500.025 | 106.83 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 988.840 | 899.657–1184.345 | 64.81 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 57.321 | 50.188–97.419 | 63.83 | equal | 17.25× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1300.018 | 1181.886–1590.925 | 66.00 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 103.287 | 88.238–126.968 | 63.12 | equal | 12.59× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 317.343 | 278.414–404.163 | 117.00 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3891.840 | 3352.280–4227.528 | 648.06 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 28300.050 | 26452.050–30939.018 | 140.48 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 623.989 | 569.741–784.362 | 128.44 | equal | 45.35× | — | — |
| pipeline_owlrl | 10000 | python-reference | 11681.572 | 11506.604–11837.617 | 149.59 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1064.587 | 903.093–1613.722 | 121.19 | equal | 10.97× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 3905.809 | 3618.814–5380.388 | 750.05 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 19.773 | 19.713–20.826 | 47.64 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.882 | 3.757–4.135 | 55.95 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.186 | 4.079–4.296 | 55.84 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 32.309 | 26.930–35.493 | 47.56 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.150 | 6.644–12.340 | 56.22 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 51.082 | 49.723–51.709 | 47.70 | reference | — | — | — |
| literal-type | 128 | python-reference | 63.407 | 60.192–65.699 | 47.58 | reference | — | — | — |
| literal-type | 128 | candidate | 7.715 | 7.153–7.788 | 56.27 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 177.353 | 169.210–198.947 | 49.20 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 15.983 | 15.384–16.432 | 58.81 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 225.685 | 218.017–256.390 | 49.50 | reference | — | — | — |
| literal-type | 512 | candidate | 21.032 | 20.264–21.386 | 59.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 28.186 | 26.082–31.774 | 62.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 333.739 | 322.110–381.074 | 51.52 | reference | — | — | — |
| literal-type | 1000 | candidate | 39.741 | 37.474–41.760 | 62.69 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 435.078 | 428.110–467.028 | 51.98 | reference | — | — | — |
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
