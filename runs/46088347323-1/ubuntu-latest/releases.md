# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T00:44:50.311480+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `1b741cc9a6cf11bbf9728db421f0e3596bbd4c2a`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 5.392 | 5.343–7.883 | 77.30 | equal | 8.98× | — | — |
| pipeline_rdfs | 100 | python-reference | 48.409 | 48.162–49.517 | 55.62 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 14.801 | 14.598–17.496 | 54.20 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 13.585 | 13.476–13.660 | 78.38 | equal | 8.39× | — | — |
| pipeline_owlrl | 100 | python-reference | 113.938 | 113.573–115.422 | 55.95 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 23.067 | 22.534–24.991 | 54.19 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 150.662 | 145.534–232.353 | 82.39 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 489.774 | 486.983–573.501 | 61.10 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 39.925 | 39.606–41.104 | 81.43 | equal | 12.27× | — | — |
| pipeline_owlrl | 1000 | python-reference | 769.304 | 766.157–866.325 | 62.24 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 88.049 | 87.297–89.198 | 82.41 | equal | 8.74× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 202.583 | 198.147–264.535 | 88.87 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 16.978 | 16.814–17.022 | 52.50 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.191 | 3.144–3.223 | 74.75 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 19.681 | 19.501–19.739 | 86.37 | reference | — | — | — |
| literal-type | 32 | candidate | 3.600 | 3.526–3.627 | 96.00 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 41.268 | 41.041–41.617 | 120.75 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 5.390 | 5.306–5.474 | 120.75 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 6.725 | 6.605–6.771 | 229.18 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 51.614 | 51.527–52.212 | 229.18 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 14.326 | 14.252–14.812 | 340.39 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 138.844 | 137.453–165.908 | 340.39 | reference | — | — | — |
| literal-type | 512 | python-reference | 183.026 | 178.884–212.759 | 656.58 | reference | — | — | — |
| literal-type | 512 | candidate | 20.341 | 19.640–20.771 | 656.58 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 272.549 | 262.028–347.766 | 1064.82 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 26.231 | 25.588–27.133 | 1064.82 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 352.175 | 349.337–357.457 | 1660.36 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.058 | 36.330–39.365 | 1660.36 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.7, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
