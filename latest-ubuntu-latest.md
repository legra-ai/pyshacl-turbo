# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T12:20:05.986810+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `f60a5103dc2e7d4e418741e6ad869bad37ff4df0`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.713 | 8.609–13.191 | 76.71 | equal | 10.35× | — | — |
| pipeline_rdfs | 100 | python-reference | 90.173 | 89.050–94.018 | 55.61 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 25.820 | 25.442–30.508 | 54.01 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.993 | 20.670–21.067 | 77.35 | equal | 10.01× | — | — |
| pipeline_owlrl | 100 | python-reference | 210.240 | 208.672–212.340 | 55.91 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 38.530 | 38.249–42.979 | 54.10 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 254.377 | 250.392–342.732 | 82.50 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 925.210 | 915.299–997.029 | 61.18 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 65.715 | 64.593–66.789 | 80.67 | equal | 14.08× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1451.394 | 1445.554–1538.180 | 62.08 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 136.678 | 133.851–137.943 | 81.28 | equal | 10.62× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 340.933 | 337.632–409.166 | 88.79 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 31.412 | 30.910–32.084 | 52.41 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.817 | 4.790–4.879 | 74.43 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 36.117 | 35.784–36.634 | 86.16 | reference | — | — | — |
| literal-type | 32 | candidate | 5.431 | 5.388–5.494 | 95.78 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 77.009 | 75.955–77.314 | 120.53 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.171 | 8.103–8.338 | 120.53 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.138 | 10.057–10.287 | 229.08 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 94.073 | 93.527–95.350 | 229.08 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 22.870 | 21.823–23.329 | 340.23 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 255.408 | 252.620–286.562 | 340.23 | reference | — | — | — |
| literal-type | 512 | python-reference | 332.811 | 329.447–365.546 | 656.38 | reference | — | — | — |
| literal-type | 512 | candidate | 30.713 | 30.060–31.204 | 656.38 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 490.830 | 485.983–560.662 | 1064.63 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 40.736 | 40.195–41.979 | 1064.63 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 635.019 | 628.631–643.997 | 1660.12 | reference | — | — | — |
| literal-type | 1000 | candidate | 57.183 | 56.086–57.495 | 1660.12 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.10, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
