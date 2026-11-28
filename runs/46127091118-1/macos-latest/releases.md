# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T09:06:11.860276+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `985a797fe6b5b0372f267476bfbaf0ff367df8d6`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 12.142 | 8.948–15.364 | 58.12 | equal | 4.94× | — | — |
| pipeline_rdfs | 100 | python-reference | 60.018 | 59.239–62.334 | 59.31 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 26.680 | 23.194–46.646 | 54.75 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 25.070 | 17.286–38.582 | 58.62 | equal | 7.38× | — | — |
| pipeline_owlrl | 100 | python-reference | 184.982 | 140.743–204.527 | 59.66 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 41.046 | 29.261–47.927 | 56.80 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 210.910 | 193.946–287.421 | 110.73 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 757.076 | 658.119–835.863 | 64.80 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 49.631 | 47.262–59.082 | 63.86 | equal | 15.25× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1280.459 | 1159.274–1399.801 | 65.92 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 136.393 | 104.650–155.381 | 63.27 | equal | 9.39× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 364.002 | 320.999–419.552 | 118.12 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 33.447 | 29.394–44.379 | 47.50 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.266 | 4.893–5.609 | 55.77 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 30.567 | 27.616–32.851 | 47.62 | reference | — | — | — |
| literal-type | 32 | candidate | 7.933 | 5.429–10.265 | 55.78 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 101.818 | 90.696–137.849 | 47.62 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 12.855 | 10.611–17.858 | 56.00 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.805 | 8.560–15.383 | 56.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 86.920 | 82.190–91.088 | 47.64 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 20.120 | 19.352–26.873 | 58.80 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 184.037 | 170.426–209.164 | 49.25 | reference | — | — | — |
| literal-type | 512 | python-reference | 274.212 | 233.866–291.583 | 49.53 | reference | — | — | — |
| literal-type | 512 | candidate | 21.299 | 20.821–26.110 | 58.89 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 374.642 | 338.889–425.797 | 51.27 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 34.829 | 31.209–62.083 | 61.95 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 666.514 | 611.324–720.143 | 52.06 | reference | — | — | — |
| literal-type | 1000 | candidate | 57.986 | 54.068–85.761 | 62.45 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.9, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
