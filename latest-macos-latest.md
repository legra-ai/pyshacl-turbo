# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T22:18:38.165321+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `fa32f201ee3f7dcda7d51af5b0978efd086ef91f`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.107 | 7.034–9.253 | 59.23 | equal | 6.63× | — | — |
| pipeline_rdfs | 100 | python-reference | 47.131 | 46.852–48.619 | 60.81 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 15.277 | 14.984–17.330 | 55.80 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 12.996 | 12.846–13.101 | 59.95 | equal | 9.76× | — | — |
| pipeline_owlrl | 100 | python-reference | 126.846 | 112.253–131.987 | 61.08 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 31.806 | 28.576–38.875 | 58.03 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 183.875 | 162.584–235.557 | 108.59 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 546.067 | 525.127–581.856 | 66.33 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 62.225 | 60.932–62.776 | 66.12 | equal | 8.78× | — | — |
| pipeline_owlrl | 1000 | python-reference | 890.915 | 861.539–999.123 | 67.39 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 83.536 | 78.221–86.694 | 64.33 | equal | 10.67× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 222.313 | 210.038–269.566 | 119.02 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 21.218 | 19.594–22.579 | 49.14 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.093 | 3.691–4.852 | 57.25 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 21.208 | 20.082–25.560 | 49.19 | reference | — | — | — |
| literal-type | 32 | candidate | 4.849 | 3.962–5.029 | 57.33 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 45.218 | 41.880–47.573 | 49.17 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.083 | 6.586–7.246 | 57.53 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.913 | 7.125–8.789 | 57.53 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 55.852 | 52.247–60.793 | 49.16 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.694 | 14.543–26.319 | 60.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 162.120 | 154.610–185.062 | 50.73 | reference | — | — | — |
| literal-type | 512 | python-reference | 226.559 | 197.001–248.973 | 51.09 | reference | — | — | — |
| literal-type | 512 | candidate | 23.221 | 21.664–23.814 | 60.25 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 321.346 | 303.887–403.221 | 52.97 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 29.447 | 28.436–29.956 | 63.30 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 388.192 | 369.246–410.282 | 53.52 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.985 | 36.632–41.213 | 63.80 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.2, rdflib-turbo 0.2.0a24

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
