# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-21T13:04:40.272057+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.757 | 9.490–9.933 | 77.13 | equal | 9.90× | — | — |
| pipeline_rdfs | 100 | python-reference | 96.605 | 95.263–100.649 | 55.58 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 28.461 | 27.927–33.912 | 54.05 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.689 | 20.421–21.228 | 78.05 | equal | 10.74× | — | — |
| pipeline_owlrl | 100 | python-reference | 222.102 | 220.434–224.888 | 55.95 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 43.497 | 42.988–47.162 | 54.03 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 289.075 | 279.109–393.288 | 82.21 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1035.728 | 1019.137–1133.728 | 61.16 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 68.472 | 65.946–69.855 | 81.25 | equal | 15.13× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1564.663 | 1549.833–1675.958 | 62.12 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 127.960 | 126.361–129.701 | 82.00 | equal | 12.23× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 386.125 | 378.139–483.662 | 88.76 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 4251.578 | 4094.581–4462.613 | 400.54 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 28101.496 | 27696.852–28673.598 | 126.50 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 799.531 | 760.015–1244.235 | 124.47 | equal | 35.15× | — | — |
| pipeline_owlrl | 10000 | python-reference | 15147.427 | 15063.731–15394.726 | 135.08 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1537.494 | 1472.190–1988.332 | 125.55 | equal | 9.85× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 6259.898 | 5932.712–6397.342 | 460.69 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.990 | 32.625–33.133 | 162.56 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.191 | 4.994–5.331 | 162.56 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 5.752 | 5.629–5.820 | 195.35 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 38.115 | 37.475–39.856 | 195.35 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.451 | 8.247–8.592 | 234.07 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 81.748 | 80.739–83.202 | 234.07 | reference | — | — | — |
| literal-type | 128 | python-reference | 100.832 | 99.973–103.714 | 322.72 | reference | — | — | — |
| literal-type | 128 | candidate | 10.394 | 10.220–10.423 | 322.72 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 273.338 | 268.872–300.312 | 433.46 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.666 | 20.808–22.295 | 433.46 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 356.272 | 353.268–403.160 | 751.16 | reference | — | — | — |
| literal-type | 512 | candidate | 28.838 | 28.224–29.771 | 751.16 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 38.951 | 38.466–39.841 | 1159.61 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 514.351 | 509.692–615.206 | 1159.61 | reference | — | — | — |
| literal-type | 1000 | candidate | 52.954 | 52.294–54.900 | 1758.32 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 683.331 | 679.352–702.877 | 1758.32 | reference | — | — | — |
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
