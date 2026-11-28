# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T09:42:37.515850+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `985a797fe6b5b0372f267476bfbaf0ff367df8d6`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 5.668 | 5.571–6.020 | 58.02 | equal | 9.28× | — | — |
| pipeline_rdfs | 100 | python-reference | 52.625 | 51.470–55.273 | 59.41 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 17.174 | 16.998–19.500 | 54.78 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 14.330 | 13.474–14.665 | 58.64 | equal | 9.05× | — | — |
| pipeline_owlrl | 100 | python-reference | 129.726 | 127.917–131.254 | 59.70 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 26.523 | 26.072–28.249 | 56.92 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 161.975 | 159.803–208.736 | 111.11 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 545.888 | 542.421–596.638 | 64.67 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 40.992 | 40.948–42.099 | 63.77 | equal | 13.32× | — | — |
| pipeline_owlrl | 1000 | python-reference | 894.646 | 877.240–950.383 | 65.91 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 76.865 | 75.256–85.280 | 63.09 | equal | 11.64× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 219.719 | 214.550–256.836 | 119.91 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 18.824 | 18.557–18.880 | 47.64 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.587 | 3.542–3.712 | 55.89 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 21.998 | 21.622–22.247 | 47.52 | reference | — | — | — |
| literal-type | 32 | candidate | 4.682 | 4.258–5.014 | 55.91 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 46.372 | 44.003–47.064 | 47.53 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 5.795 | 5.670–5.860 | 56.11 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.003 | 6.532–7.211 | 56.23 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 57.121 | 56.620–57.760 | 47.67 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 14.364 | 14.167–14.651 | 58.73 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 156.809 | 154.378–191.139 | 49.11 | reference | — | — | — |
| literal-type | 512 | python-reference | 197.297 | 195.857–219.814 | 49.69 | reference | — | — | — |
| literal-type | 512 | candidate | 18.916 | 18.348–19.242 | 58.94 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 301.989 | 291.891–349.411 | 51.52 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 24.952 | 24.472–25.336 | 62.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 408.578 | 374.720–450.179 | 52.05 | reference | — | — | — |
| literal-type | 1000 | candidate | 35.274 | 31.659–38.630 | 62.59 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.9, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
