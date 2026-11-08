# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-08T16:29:03.700137+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `74fb5c25dde149710047215b55bc9b3ccafd257d`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.012 | 6.656–15.960 | 57.88 | equal | 9.14× | — | — |
| pipeline_rdfs | 100 | python-reference | 64.096 | 60.001–66.008 | 59.34 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 19.405 | 19.158–23.654 | 54.80 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 24.740 | 20.702–36.245 | 58.36 | equal | 6.06× | — | — |
| pipeline_owlrl | 100 | python-reference | 149.954 | 145.008–165.972 | 59.61 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 40.294 | 34.467–41.927 | 56.81 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 196.220 | 183.545–269.711 | 109.58 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 648.837 | 626.707–731.175 | 64.86 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 54.811 | 48.212–73.896 | 63.78 | equal | 11.84× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1111.276 | 1045.128–1308.417 | 65.95 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 115.726 | 96.298–142.233 | 62.78 | equal | 9.60× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 392.567 | 265.899–481.183 | 118.38 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 21.274 | 20.902–22.310 | 47.62 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.408 | 4.231–4.571 | 55.67 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 24.509 | 24.318–25.090 | 47.66 | reference | — | — | — |
| literal-type | 32 | candidate | 7.609 | 4.764–10.387 | 55.72 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 54.163 | 51.266–60.702 | 47.70 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.776 | 6.679–7.448 | 55.95 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.059 | 7.869–8.307 | 56.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 67.860 | 65.732–74.699 | 47.69 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.031 | 16.716–18.710 | 58.62 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 191.582 | 175.055–238.462 | 49.31 | reference | — | — | — |
| literal-type | 512 | python-reference | 232.522 | 230.147–281.625 | 49.56 | reference | — | — | — |
| literal-type | 512 | candidate | 25.768 | 21.674–30.289 | 58.88 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 424.461 | 351.241–496.910 | 51.55 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 32.090 | 30.475–36.575 | 61.98 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 504.943 | 433.195–654.694 | 52.09 | reference | — | — | — |
| literal-type | 1000 | candidate | 53.423 | 51.482–70.402 | 62.31 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.10.1, rdflib-turbo 0.2.0a37

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
