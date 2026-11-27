# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-27T10:58:57.878782+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `3f319829314500ac13004046836a74c68210dcdb`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 6.548 | 6.437–9.303 | 58.09 | equal | 8.90× | — | — |
| pipeline_rdfs | 100 | python-reference | 58.310 | 57.659–62.154 | 59.41 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 22.616 | 19.442–25.725 | 54.59 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.409 | 16.662–19.358 | 58.62 | equal | 8.11× | — | — |
| pipeline_owlrl | 100 | python-reference | 141.149 | 138.676–148.744 | 59.73 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 33.927 | 29.057–34.812 | 56.91 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 194.325 | 177.217–245.382 | 109.70 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 708.425 | 628.852–739.078 | 64.94 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 55.528 | 49.578–66.806 | 63.69 | equal | 12.76× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1055.139 | 984.128–1081.133 | 66.08 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 87.505 | 85.126–93.305 | 63.16 | equal | 12.06× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 256.711 | 243.893–316.994 | 118.81 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 22.623 | 22.254–25.159 | 47.62 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.045 | 3.976–4.167 | 55.88 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 23.869 | 23.326–26.243 | 47.61 | reference | — | — | — |
| literal-type | 32 | candidate | 4.447 | 4.392–4.830 | 55.81 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 56.951 | 54.646–76.207 | 47.64 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.590 | 6.443–8.938 | 56.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.722 | 8.057–9.324 | 56.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 70.013 | 65.007–79.490 | 47.62 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.154 | 15.606–20.655 | 58.72 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 190.777 | 173.329–210.654 | 49.25 | reference | — | — | — |
| literal-type | 512 | python-reference | 260.229 | 228.021–302.878 | 49.55 | reference | — | — | — |
| literal-type | 512 | candidate | 23.541 | 23.220–25.260 | 59.02 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 381.542 | 328.878–496.640 | 51.48 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 28.442 | 27.940–29.765 | 62.03 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 430.819 | 426.495–640.398 | 52.03 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.584 | 37.436–42.839 | 62.56 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.5, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
