# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T07:58:05.391742+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `803b555b073e68cd471cca1ecdfa05969f88d857`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.004 | 6.681–10.418 | 57.95 | equal | 12.74× | — | — |
| pipeline_rdfs | 100 | python-reference | 89.220 | 59.620–119.635 | 59.34 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 22.422 | 19.149–30.210 | 54.66 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.987 | 15.250–17.283 | 58.45 | equal | 8.50× | — | — |
| pipeline_owlrl | 100 | python-reference | 135.917 | 134.755–142.919 | 59.61 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 28.206 | 27.514–31.085 | 56.89 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 218.960 | 200.185–355.917 | 109.78 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 651.111 | 599.010–695.790 | 64.89 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 44.349 | 43.441–46.900 | 63.83 | equal | 14.68× | — | — |
| pipeline_owlrl | 1000 | python-reference | 972.425 | 942.068–1275.166 | 65.98 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 103.870 | 97.588–158.193 | 63.31 | equal | 9.36× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 248.273 | 240.636–303.486 | 119.08 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 20.260 | 20.020–21.296 | 47.53 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.980 | 3.963–4.533 | 55.78 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 26.038 | 24.911–27.783 | 47.56 | reference | — | — | — |
| literal-type | 32 | candidate | 4.761 | 4.357–4.934 | 55.78 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 49.057 | 48.537–51.058 | 47.66 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.332 | 6.232–7.488 | 56.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.303 | 7.604–9.343 | 56.06 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 62.323 | 60.888–71.863 | 47.53 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.006 | 15.693–22.090 | 58.72 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 176.725 | 166.766–191.548 | 49.25 | reference | — | — | — |
| literal-type | 512 | python-reference | 223.950 | 217.396–249.921 | 49.56 | reference | — | — | — |
| literal-type | 512 | candidate | 20.704 | 20.457–23.882 | 59.06 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 350.368 | 328.277–406.767 | 51.47 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 31.115 | 28.994–34.041 | 61.95 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 564.797 | 466.336–728.106 | 52.06 | reference | — | — | — |
| literal-type | 1000 | candidate | 53.029 | 48.550–83.299 | 62.48 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.8, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
