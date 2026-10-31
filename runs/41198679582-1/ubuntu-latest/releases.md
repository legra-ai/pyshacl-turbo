# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T12:09:36.895680+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `339ed12bacf19872195caf04e4c98e64182fadee`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 13.595 | 13.210–13.840 | 64.45 | equal | 9.52× | — | — |
| pipeline_rdfs | 100 | python-reference | 129.409 | 128.815–130.714 | 47.39 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 33.198 | 32.743–38.438 | 44.45 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.022 | 22.829–23.476 | 65.72 | equal | 13.58× | — | — |
| pipeline_owlrl | 100 | python-reference | 312.569 | 311.215–320.994 | 47.64 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 50.344 | 48.796–54.120 | 45.41 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 330.339 | 316.991–421.724 | 73.95 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1287.721 | 1279.376–1353.016 | 52.75 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 104.794 | 102.989–106.719 | 70.12 | equal | 12.29× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2188.590 | 2150.912–2271.608 | 53.94 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 144.359 | 141.497–256.771 | 69.63 | equal | 15.16× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 432.746 | 420.434–497.751 | 80.46 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 47.099 | 46.709–48.503 | 42.59 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.308 | 5.186–5.411 | 63.40 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 55.090 | 54.579–56.033 | 76.59 | reference | — | — | — |
| literal-type | 32 | candidate | 5.922 | 5.810–6.151 | 86.21 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 115.331 | 114.148–117.097 | 110.84 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.030 | 8.867–9.190 | 110.84 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.193 | 11.016–11.237 | 219.01 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 141.936 | 140.433–144.180 | 219.01 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 23.998 | 23.555–24.148 | 330.34 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 384.156 | 380.072–415.639 | 330.34 | reference | — | — | — |
| literal-type | 512 | python-reference | 496.692 | 492.196–538.568 | 646.82 | reference | — | — | — |
| literal-type | 512 | candidate | 32.517 | 32.108–32.747 | 646.82 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 724.694 | 715.328–797.809 | 1055.09 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 43.134 | 42.572–43.965 | 1055.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 953.484 | 938.754–993.672 | 1650.14 | reference | — | — | — |
| literal-type | 1000 | candidate | 58.952 | 58.820–59.852 | 1650.14 | different | — | logical_inplace_owlrl_different | — |
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
