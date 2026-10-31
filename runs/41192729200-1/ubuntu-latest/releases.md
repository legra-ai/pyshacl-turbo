# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T10:43:10.559916+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `9aa243c37b1ff06d6481b38f55f0b6bb29e09306`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 14.274 | 13.983–14.464 | 64.41 | equal | 9.24× | — | — |
| pipeline_rdfs | 100 | python-reference | 131.827 | 131.149–133.191 | 47.41 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 34.888 | 34.269–40.378 | 44.27 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.604 | 23.205–23.782 | 65.61 | equal | 13.49× | — | — |
| pipeline_owlrl | 100 | python-reference | 318.306 | 315.130–319.911 | 47.60 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 52.080 | 50.816–55.640 | 45.38 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 341.892 | 330.455–451.178 | 74.03 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1294.183 | 1290.268–1374.126 | 52.89 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 105.634 | 104.689–108.572 | 70.04 | equal | 12.25× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2186.779 | 2171.026–2302.969 | 53.83 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 141.114 | 139.744–202.342 | 69.58 | equal | 15.50× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 445.742 | 434.021–532.676 | 80.56 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 4713.721 | 4473.573–4840.397 | 392.23 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 28477.326 | 28336.547–28729.029 | 118.46 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 1430.610 | 1374.202–1471.847 | 117.03 | equal | 19.91× | — | — |
| pipeline_owlrl | 10000 | python-reference | 21431.167 | 21202.601–21743.985 | 126.54 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1790.074 | 1711.184–2320.138 | 102.84 | equal | 11.97× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 6429.136 | 6349.994–6748.738 | 449.92 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 47.224 | 46.754–48.518 | 164.16 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.663 | 5.458–5.703 | 164.16 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 6.152 | 6.028–6.406 | 196.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 54.799 | 54.292–56.488 | 196.97 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.211 | 9.106–9.354 | 235.59 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 115.080 | 114.481–118.296 | 235.59 | reference | — | — | — |
| literal-type | 128 | python-reference | 146.575 | 144.266–148.611 | 324.29 | reference | — | — | — |
| literal-type | 128 | candidate | 11.563 | 11.324–11.709 | 324.29 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 388.523 | 385.537–424.996 | 435.10 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 24.382 | 24.220–24.464 | 435.10 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 500.935 | 497.438–554.712 | 748.70 | reference | — | — | — |
| literal-type | 512 | candidate | 32.747 | 32.345–33.206 | 748.70 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 44.271 | 42.946–45.489 | 1150.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 748.855 | 735.769–839.757 | 1150.09 | reference | — | — | — |
| literal-type | 1000 | candidate | 59.565 | 58.769–60.055 | 1748.91 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 972.883 | 953.637–986.458 | 1748.91 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.0, rdflib-turbo 0.2.0a20

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
