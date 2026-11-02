# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-02T17:58:29.806837+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `1fbe159029984365ffc705388cc1e2b33280c415`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.554 | 8.401–8.846 | 66.37 | equal | 8.02× | — | — |
| pipeline_rdfs | 100 | python-reference | 68.567 | 68.426–69.921 | 47.32 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 18.745 | 18.278–21.912 | 44.28 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.196 | 16.088–16.427 | 66.64 | equal | 11.15× | — | — |
| pipeline_owlrl | 100 | python-reference | 180.508 | 166.437–194.366 | 47.63 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 28.095 | 27.696–30.150 | 45.43 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 186.553 | 180.623–286.171 | 74.08 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 683.911 | 666.537–743.562 | 52.84 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 66.232 | 64.230–69.309 | 71.94 | equal | 10.33× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1157.774 | 1119.299–1235.924 | 53.92 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 106.936 | 101.087–205.621 | 70.61 | equal | 10.83× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 247.113 | 243.563–344.865 | 80.31 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 25.392 | 24.784–26.070 | 42.97 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.707 | 3.658–3.784 | 64.39 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 29.090 | 28.662–29.467 | 76.72 | reference | — | — | — |
| literal-type | 32 | candidate | 4.186 | 4.119–5.064 | 86.22 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 60.385 | 57.729–61.496 | 110.97 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.377 | 6.316–6.487 | 110.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.935 | 7.622–8.086 | 219.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 73.490 | 72.407–76.322 | 219.12 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.896 | 16.669–17.112 | 330.34 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 206.900 | 196.135–240.250 | 330.34 | reference | — | — | — |
| literal-type | 512 | python-reference | 258.849 | 254.899–299.131 | 647.00 | reference | — | — | — |
| literal-type | 512 | candidate | 23.512 | 22.568–23.681 | 647.00 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 383.011 | 370.209–465.078 | 1055.20 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 31.411 | 29.884–31.901 | 1055.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 503.104 | 491.725–508.794 | 1650.14 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.624 | 43.119–44.576 | 1650.14 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.8.0, rdflib-turbo 0.2.0a30

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
