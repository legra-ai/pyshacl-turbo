# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T12:56:51.976624+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `339ed12bacf19872195caf04e4c98e64182fadee`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 11.128 | 10.884–11.632 | 64.37 | equal | 8.66× | — | — |
| pipeline_rdfs | 100 | python-reference | 96.412 | 95.496–97.023 | 47.35 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 25.732 | 25.134–31.069 | 44.15 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.961 | 18.585–19.721 | 65.66 | equal | 12.22× | — | — |
| pipeline_owlrl | 100 | python-reference | 231.744 | 228.172–235.884 | 47.55 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 39.760 | 39.491–43.171 | 45.32 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 258.921 | 252.743–353.758 | 73.66 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 951.246 | 944.754–1038.130 | 52.75 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 86.082 | 85.098–88.023 | 70.15 | equal | 11.05× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1612.269 | 1586.949–1700.137 | 53.93 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 118.619 | 116.580–218.407 | 69.53 | equal | 13.59× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 347.278 | 340.189–443.850 | 80.28 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 34.965 | 34.743–37.287 | 42.86 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.414 | 4.326–4.522 | 63.45 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 40.702 | 40.504–41.223 | 76.61 | reference | — | — | — |
| literal-type | 32 | candidate | 4.907 | 4.770–5.019 | 86.11 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 85.737 | 85.020–87.109 | 110.86 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.534 | 7.454–7.635 | 110.86 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.257 | 9.107–9.326 | 219.03 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 108.744 | 107.638–109.177 | 219.03 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.784 | 19.535–20.414 | 330.35 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 283.710 | 282.651–318.086 | 330.35 | reference | — | — | — |
| literal-type | 512 | python-reference | 367.894 | 366.403–413.981 | 646.83 | reference | — | — | — |
| literal-type | 512 | candidate | 26.986 | 26.510–27.303 | 646.83 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 537.640 | 535.904–620.207 | 1055.20 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 35.964 | 35.644–36.744 | 1055.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 713.842 | 704.319–718.079 | 1650.14 | reference | — | — | — |
| literal-type | 1000 | candidate | 49.112 | 48.723–50.413 | 1650.14 | different | — | logical_inplace_owlrl_different | — |
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
