# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T13:51:57.898707+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `5be2fd5b65a8200bb299b744f781034fa902baff`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.040 | 8.795–12.406 | 76.72 | equal | 10.74× | — | — |
| pipeline_rdfs | 100 | python-reference | 97.062 | 95.009–99.340 | 55.64 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.236 | 26.873–31.869 | 54.03 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 19.724 | 19.496–19.995 | 77.30 | equal | 11.15× | — | — |
| pipeline_owlrl | 100 | python-reference | 219.828 | 218.536–224.462 | 55.96 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 41.821 | 41.292–44.876 | 54.08 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 274.310 | 263.340–353.989 | 82.32 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1005.578 | 992.468–1073.089 | 61.09 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 65.492 | 64.395–68.243 | 80.75 | equal | 15.35× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1536.662 | 1520.075–1619.323 | 62.22 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 125.157 | 122.878–132.109 | 81.26 | equal | 12.28× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 355.920 | 349.903–424.696 | 88.88 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3627.414 | 3576.501–3846.328 | 400.60 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 27690.345 | 27576.536–28123.380 | 126.33 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 719.482 | 706.973–738.096 | 123.96 | equal | 38.49× | — | — |
| pipeline_owlrl | 10000 | python-reference | 15007.424 | 14949.650–15087.316 | 134.56 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1265.404 | 1241.630–1616.559 | 124.67 | equal | 11.86× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5180.274 | 5094.021–5363.726 | 458.56 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.599 | 32.309–32.875 | 169.39 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.870 | 4.761–4.931 | 169.39 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 5.400 | 5.276–5.441 | 202.23 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 38.561 | 38.076–39.399 | 202.23 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.000 | 7.914–8.122 | 240.87 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 79.599 | 79.441–80.322 | 240.87 | reference | — | — | — |
| literal-type | 128 | python-reference | 98.246 | 97.551–98.905 | 329.50 | reference | — | — | — |
| literal-type | 128 | candidate | 9.938 | 9.755–9.988 | 329.50 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 269.479 | 267.559–299.610 | 440.24 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 20.950 | 20.386–21.397 | 440.24 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 346.636 | 342.674–375.000 | 753.54 | reference | — | — | — |
| literal-type | 512 | candidate | 28.385 | 27.835–28.601 | 753.54 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 37.608 | 37.092–38.126 | 1159.30 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 506.066 | 503.073–570.589 | 1159.30 | reference | — | — | — |
| literal-type | 1000 | candidate | 51.663 | 51.181–52.397 | 1753.59 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 661.675 | 653.500–669.068 | 1753.59 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.11, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
