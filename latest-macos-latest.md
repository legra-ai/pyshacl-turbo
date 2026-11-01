# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-01T12:52:02.309833+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `e5164a97129fa57013b0359b374bebecd333368b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.150 | 7.973–10.296 | 59.30 | equal | 6.46× | — | — |
| pipeline_rdfs | 100 | python-reference | 52.658 | 52.107–54.505 | 60.83 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 17.003 | 16.685–19.431 | 55.97 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 14.916 | 14.803–15.651 | 59.84 | equal | 8.57× | — | — |
| pipeline_owlrl | 100 | python-reference | 127.891 | 127.049–129.093 | 61.12 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 26.250 | 25.862–28.303 | 58.05 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 161.114 | 158.104–206.203 | 110.16 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 547.626 | 545.759–615.511 | 66.36 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 61.752 | 61.092–62.022 | 65.84 | equal | 8.87× | — | — |
| pipeline_owlrl | 1000 | python-reference | 886.521 | 875.130–944.170 | 67.52 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 85.933 | 85.398–100.272 | 64.36 | equal | 10.32× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 212.561 | 212.066–251.799 | 119.59 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 2374.292 | 2220.370–2971.580 | 682.09 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 15526.213 | 14259.750–16138.894 | 142.09 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 655.904 | 652.668–876.262 | 142.22 | equal | 23.67× | — | — |
| pipeline_owlrl | 10000 | python-reference | 8909.833 | 8692.992–9064.702 | 151.17 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 880.093 | 878.825–1108.089 | 122.73 | equal | 10.12× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 3168.341 | 3127.400–3273.299 | 781.73 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 18.975 | 18.932–19.316 | 49.20 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.781 | 3.757–3.803 | 57.11 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.225 | 4.216–4.359 | 57.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.027 | 21.832–22.083 | 49.14 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.295 | 6.237–6.390 | 57.42 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 46.370 | 46.161–46.886 | 49.19 | reference | — | — | — |
| literal-type | 128 | python-reference | 57.379 | 56.849–64.900 | 49.16 | reference | — | — | — |
| literal-type | 128 | candidate | 8.602 | 7.737–9.067 | 57.45 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 157.369 | 156.301–178.245 | 50.67 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.096 | 16.042–16.271 | 59.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 205.486 | 200.538–229.339 | 51.06 | reference | — | — | — |
| literal-type | 512 | candidate | 21.559 | 21.498–21.728 | 60.28 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 28.564 | 28.221–28.917 | 63.16 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 298.926 | 292.435–346.448 | 52.97 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.573 | 38.485–45.306 | 63.64 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 383.706 | 381.472–391.492 | 53.56 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.4, rdflib-turbo 0.2.0a24

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
