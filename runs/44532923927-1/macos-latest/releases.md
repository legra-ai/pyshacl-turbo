# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-19T14:15:46.854517+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.292 | 6.366–9.418 | 58.06 | equal | 7.87× | — | — |
| pipeline_rdfs | 100 | python-reference | 57.414 | 55.965–74.992 | 59.38 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.581 | 18.315–23.568 | 54.66 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.659 | 15.902–18.901 | 58.61 | equal | 10.44× | — | — |
| pipeline_owlrl | 100 | python-reference | 173.982 | 148.170–242.254 | 59.69 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 33.889 | 33.448–44.250 | 56.84 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 250.873 | 203.543–393.242 | 110.42 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 666.219 | 642.688–729.929 | 64.92 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 46.532 | 44.444–55.654 | 63.69 | equal | 14.32× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1072.298 | 1033.573–1249.496 | 66.06 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 101.399 | 92.742–112.819 | 63.17 | equal | 10.57× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 319.683 | 261.200–343.103 | 119.92 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3240.714 | 2999.392–3522.392 | 683.08 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 20759.368 | 19312.543–34151.327 | 140.56 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 601.418 | 534.881–1243.048 | 128.20 | equal | 34.52× | — | — |
| pipeline_owlrl | 10000 | python-reference | 13584.518 | 11343.327–14585.501 | 149.72 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1208.613 | 961.355–1462.409 | 121.59 | equal | 11.24× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 4975.832 | 4629.056–5146.804 | 743.16 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 23.074 | 20.617–23.413 | 47.70 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.018 | 3.897–4.655 | 55.91 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 9.605 | 5.197–12.273 | 55.84 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 24.197 | 23.241–26.661 | 47.61 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.319 | 6.200–7.434 | 56.17 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 53.928 | 51.886–70.926 | 47.62 | reference | — | — | — |
| literal-type | 128 | python-reference | 67.371 | 63.218–71.682 | 47.66 | reference | — | — | — |
| literal-type | 128 | candidate | 8.210 | 7.675–8.574 | 56.23 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 224.687 | 195.732–259.931 | 49.27 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.775 | 15.347–20.000 | 58.75 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 272.151 | 229.930–332.724 | 49.59 | reference | — | — | — |
| literal-type | 512 | candidate | 24.277 | 21.995–29.742 | 59.05 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 30.960 | 28.396–37.868 | 62.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 360.615 | 331.680–430.257 | 51.50 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.157 | 38.857–49.074 | 62.53 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 605.796 | 475.656–724.465 | 52.08 | reference | — | — | — |
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
