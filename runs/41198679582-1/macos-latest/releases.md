# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T12:12:52.825980+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `339ed12bacf19872195caf04e4c98e64182fadee`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 11.984 | 9.837–15.507 | 59.22 | equal | 6.22× | — | — |
| pipeline_rdfs | 100 | python-reference | 74.505 | 60.127–84.133 | 60.83 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 19.528 | 18.769–21.448 | 55.72 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.941 | 17.571–19.878 | 59.80 | equal | 8.69× | — | — |
| pipeline_owlrl | 100 | python-reference | 155.842 | 142.150–187.318 | 61.03 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 30.322 | 28.893–32.723 | 58.02 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 218.443 | 185.144–305.174 | 108.17 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 636.034 | 615.417–674.256 | 66.41 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 73.180 | 70.065–75.310 | 66.12 | equal | 8.69× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1016.866 | 996.985–1091.347 | 67.55 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 106.554 | 104.312–140.038 | 64.27 | equal | 9.54× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 262.432 | 249.874–330.725 | 119.83 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 20.726 | 20.573–21.099 | 49.17 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.603 | 4.458–5.056 | 57.05 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.118 | 25.381–29.441 | 49.11 | reference | — | — | — |
| literal-type | 32 | candidate | 5.044 | 4.971–5.162 | 57.05 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 53.987 | 51.924–56.919 | 49.09 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.709 | 7.261–10.880 | 57.34 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.044 | 8.707–9.572 | 57.36 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 67.171 | 64.670–74.037 | 49.12 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.649 | 19.997–24.066 | 59.83 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 185.029 | 170.408–209.620 | 50.70 | reference | — | — | — |
| literal-type | 512 | python-reference | 229.581 | 221.786–263.698 | 51.03 | reference | — | — | — |
| literal-type | 512 | candidate | 24.987 | 24.711–29.502 | 60.16 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 344.422 | 332.688–418.013 | 52.98 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 34.681 | 31.850–35.453 | 63.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 442.734 | 431.096–464.017 | 53.52 | reference | — | — | — |
| literal-type | 1000 | candidate | 44.607 | 43.048–49.645 | 63.61 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.1, rdflib-turbo 0.2.0a23

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
