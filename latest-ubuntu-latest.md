# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-03T22:43:31.628550+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `b36b227b1766aee5397e3ff30b3076741e5fefdf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.046 | 6.892–7.278 | 66.35 | equal | 10.22× | — | — |
| pipeline_rdfs | 100 | python-reference | 72.030 | 70.861–72.649 | 47.34 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 22.858 | 20.834–32.107 | 44.23 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.331 | 18.000–18.681 | 66.73 | equal | 9.73× | — | — |
| pipeline_owlrl | 100 | python-reference | 178.378 | 176.846–181.492 | 47.67 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 31.989 | 31.233–35.696 | 45.34 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 222.535 | 210.471–386.483 | 73.78 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 745.051 | 724.072–871.802 | 52.83 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 48.290 | 46.339–51.808 | 71.18 | equal | 15.43× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1258.829 | 1225.327–1429.466 | 53.96 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 119.305 | 115.042–229.296 | 70.72 | equal | 10.55× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 326.458 | 317.766–459.102 | 80.15 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 25.952 | 25.543–28.356 | 42.76 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.312 | 4.279–4.332 | 64.74 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 30.324 | 30.164–30.577 | 76.64 | reference | — | — | — |
| literal-type | 32 | candidate | 4.856 | 4.775–5.041 | 86.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 64.151 | 63.291–64.441 | 110.76 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.394 | 7.210–7.548 | 110.76 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.093 | 8.914–9.153 | 218.93 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 80.752 | 79.511–86.087 | 218.93 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.048 | 18.657–19.445 | 330.36 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 221.095 | 219.302–304.267 | 330.36 | reference | — | — | — |
| literal-type | 512 | python-reference | 287.376 | 283.913–427.008 | 646.89 | reference | — | — | — |
| literal-type | 512 | candidate | 26.190 | 25.816–26.614 | 646.89 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 411.453 | 409.267–562.390 | 1055.16 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 35.428 | 34.057–36.536 | 1055.16 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 537.069 | 524.317–560.727 | 1650.15 | reference | — | — | — |
| literal-type | 1000 | candidate | 46.655 | 46.159–48.436 | 1650.15 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.10.0, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
