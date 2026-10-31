# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T08:47:45.115971+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `9aa243c37b1ff06d6481b38f55f0b6bb29e09306`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 13.897 | 13.433–13.990 | 64.54 | equal | 9.37× | — | — |
| pipeline_rdfs | 100 | python-reference | 130.268 | 129.036–131.710 | 47.43 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 34.173 | 33.894–39.311 | 44.23 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.613 | 23.520–23.883 | 65.58 | equal | 13.21× | — | — |
| pipeline_owlrl | 100 | python-reference | 312.000 | 309.610–320.822 | 47.54 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 50.151 | 49.324–55.019 | 45.41 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 329.904 | 319.145–426.331 | 73.86 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1282.153 | 1276.592–1363.824 | 52.89 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 104.708 | 103.953–106.994 | 70.00 | equal | 12.25× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2179.484 | 2144.799–2265.764 | 53.98 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 139.837 | 137.613–205.521 | 69.58 | equal | 15.59× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 431.434 | 423.564–506.897 | 80.34 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 49.484 | 49.003–50.603 | 42.93 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.423 | 5.209–5.595 | 63.42 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 54.972 | 54.182–55.731 | 76.68 | reference | — | — | — |
| literal-type | 32 | candidate | 6.075 | 5.965–6.253 | 86.18 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 116.717 | 116.285–118.828 | 110.80 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.293 | 9.146–9.345 | 110.80 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.452 | 11.295–11.583 | 219.05 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 143.717 | 142.787–145.179 | 219.05 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 24.190 | 23.693–24.414 | 330.33 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 390.916 | 386.498–422.559 | 330.33 | reference | — | — | — |
| literal-type | 512 | python-reference | 496.254 | 491.269–531.151 | 646.92 | reference | — | — | — |
| literal-type | 512 | candidate | 32.662 | 32.119–33.191 | 646.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 733.786 | 727.203–842.158 | 1055.20 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 44.365 | 43.377–45.125 | 1055.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 963.737 | 952.295–986.709 | 1650.32 | reference | — | — | — |
| literal-type | 1000 | candidate | 60.208 | 59.514–60.876 | 1650.32 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.0, rdflib-turbo 0.2.0a20

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
