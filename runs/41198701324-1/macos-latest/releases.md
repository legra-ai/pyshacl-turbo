# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T13:05:00.462087+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `339ed12bacf19872195caf04e4c98e64182fadee`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 11.624 | 10.141–18.473 | 59.22 | equal | 5.55× | — | — |
| pipeline_rdfs | 100 | python-reference | 64.459 | 60.852–73.101 | 60.75 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.632 | 20.715–25.795 | 55.94 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.788 | 15.349–19.005 | 59.73 | equal | 7.52× | — | — |
| pipeline_owlrl | 100 | python-reference | 141.373 | 129.169–157.736 | 61.05 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 27.579 | 26.506–28.719 | 58.11 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 230.711 | 165.430–362.897 | 111.08 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 670.092 | 596.959–714.739 | 66.28 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 66.402 | 64.415–94.971 | 66.12 | equal | 10.09× | — | — |
| pipeline_owlrl | 1000 | python-reference | 997.829 | 915.454–1237.721 | 67.36 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 121.697 | 89.891–126.083 | 64.16 | equal | 8.20× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 272.856 | 239.505–304.838 | 121.28 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 22.727 | 20.860–34.411 | 48.97 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.798 | 4.758–5.072 | 57.03 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 44.479 | 35.638–58.316 | 49.06 | reference | — | — | — |
| literal-type | 32 | candidate | 5.187 | 4.745–6.127 | 57.03 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 61.651 | 59.859–63.884 | 49.06 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 10.290 | 8.926–11.462 | 57.28 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.940 | 10.429–11.837 | 57.39 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 108.981 | 95.810–139.020 | 49.03 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 28.131 | 21.016–40.507 | 59.83 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 215.339 | 198.892–239.719 | 50.67 | reference | — | — | — |
| literal-type | 512 | python-reference | 239.943 | 233.058–272.538 | 50.95 | reference | — | — | — |
| literal-type | 512 | candidate | 27.220 | 22.338–32.995 | 60.12 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 370.181 | 335.496–521.127 | 52.89 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 42.578 | 39.537–43.275 | 63.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 515.622 | 444.156–565.339 | 53.41 | reference | — | — | — |
| literal-type | 1000 | candidate | 54.576 | 46.030–58.185 | 63.61 | different | — | logical_inplace_owlrl_different | — |
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
