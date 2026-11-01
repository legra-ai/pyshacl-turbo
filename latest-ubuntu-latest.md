# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-01T12:20:27.686315+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `e5164a97129fa57013b0359b374bebecd333368b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 13.855 | 13.789–14.671 | 64.46 | equal | 9.41× | — | — |
| pipeline_rdfs | 100 | python-reference | 130.327 | 128.347–132.872 | 47.30 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 34.288 | 33.924–40.227 | 44.41 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.962 | 23.235–24.288 | 65.39 | equal | 13.10× | — | — |
| pipeline_owlrl | 100 | python-reference | 313.911 | 311.817–319.769 | 47.70 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 50.728 | 49.081–52.975 | 45.55 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 339.263 | 329.378–453.939 | 73.96 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1306.029 | 1288.372–1375.589 | 52.84 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 102.640 | 102.263–105.216 | 70.01 | equal | 12.72× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2181.445 | 2168.790–2289.437 | 53.94 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 142.631 | 139.711–205.580 | 70.37 | equal | 15.29× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 443.704 | 433.421–537.146 | 80.36 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 4721.576 | 4574.369–4901.819 | 392.31 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 28128.117 | 27915.838–28283.566 | 118.59 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 1213.326 | 1201.155–1221.549 | 117.11 | equal | 23.18× | — | — |
| pipeline_owlrl | 10000 | python-reference | 21049.362 | 20734.325–21275.816 | 126.61 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1542.653 | 1503.508–1854.337 | 111.41 | equal | 13.64× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5865.152 | 5827.936–5958.965 | 450.27 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 48.834 | 48.146–50.028 | 152.48 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.420 | 5.354–5.597 | 152.48 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 5.962 | 5.871–6.030 | 185.30 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 54.813 | 54.348–55.488 | 185.30 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.072 | 8.987–9.279 | 224.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 114.271 | 113.742–115.176 | 224.09 | reference | — | — | — |
| literal-type | 128 | python-reference | 143.403 | 141.803–144.838 | 312.75 | reference | — | — | — |
| literal-type | 128 | candidate | 11.155 | 11.091–11.507 | 312.75 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 385.695 | 382.150–417.321 | 438.44 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 24.005 | 23.672–24.291 | 438.44 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 496.156 | 492.691–526.355 | 750.58 | reference | — | — | — |
| literal-type | 512 | candidate | 32.486 | 32.020–32.783 | 750.58 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 43.066 | 42.775–44.012 | 1150.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 724.951 | 717.055–815.565 | 1150.14 | reference | — | — | — |
| literal-type | 1000 | candidate | 59.035 | 58.888–60.616 | 1748.79 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 953.821 | 943.403–965.514 | 1748.79 | reference | — | — | — |
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
