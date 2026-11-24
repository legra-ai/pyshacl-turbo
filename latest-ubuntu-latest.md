# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-24T15:12:17.584433+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.951 | 7.884–8.210 | 76.54 | equal | 8.65× | — | — |
| pipeline_rdfs | 100 | python-reference | 68.752 | 68.153–81.516 | 55.68 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 22.493 | 22.335–26.911 | 54.29 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.915 | 16.694–17.616 | 77.34 | equal | 9.72× | — | — |
| pipeline_owlrl | 100 | python-reference | 164.395 | 163.354–166.794 | 55.90 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.778 | 34.055–37.871 | 54.43 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 230.857 | 225.967–371.615 | 82.55 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 731.045 | 724.211–878.171 | 61.09 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 56.050 | 53.491–57.661 | 80.62 | equal | 13.04× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1150.030 | 1141.229–1329.688 | 62.12 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 107.027 | 106.438–111.153 | 81.29 | equal | 10.75× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 311.340 | 300.442–447.483 | 88.78 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3895.008 | 3653.958–4027.425 | 400.44 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 20031.476 | 19890.255–20571.189 | 126.45 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 758.603 | 688.119–1201.185 | 123.89 | equal | 26.41× | — | — |
| pipeline_owlrl | 10000 | python-reference | 11678.700 | 11594.911–12084.187 | 134.57 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1448.831 | 1396.249–1961.843 | 124.87 | equal | 8.06× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5428.909 | 5201.594–5596.889 | 459.12 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.162 | 23.924–24.844 | 169.54 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.005 | 3.990–4.061 | 169.54 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.559 | 4.444–4.737 | 202.30 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.865 | 27.400–28.231 | 202.30 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.872 | 6.801–6.996 | 240.95 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 59.917 | 59.326–62.001 | 240.95 | reference | — | — | — |
| literal-type | 128 | python-reference | 74.622 | 73.630–74.887 | 329.61 | reference | — | — | — |
| literal-type | 128 | candidate | 8.298 | 8.257–8.456 | 329.61 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 202.931 | 199.392–250.106 | 440.31 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.391 | 17.247–17.586 | 440.31 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 262.338 | 258.374–305.942 | 753.52 | reference | — | — | — |
| literal-type | 512 | candidate | 23.569 | 23.068–23.897 | 753.52 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 31.346 | 31.196–31.875 | 1159.37 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 381.965 | 377.884–482.814 | 1159.37 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.429 | 42.894–44.112 | 1753.72 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 497.729 | 491.505–521.133 | 1753.72 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
