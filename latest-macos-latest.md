# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T11:32:56.540504+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `f60a5103dc2e7d4e418741e6ad869bad37ff4df0`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.528 | 7.154–13.417 | 58.09 | equal | 5.56× | — | — |
| pipeline_rdfs | 100 | python-reference | 58.550 | 56.678–63.746 | 59.27 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 28.712 | 21.935–36.481 | 54.59 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.030 | 15.053–17.669 | 58.64 | equal | 9.99× | — | — |
| pipeline_owlrl | 100 | python-reference | 160.143 | 150.792–168.623 | 59.55 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.346 | 30.116–36.274 | 56.83 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 258.936 | 213.656–310.254 | 110.84 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 692.873 | 618.356–795.039 | 64.81 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 53.840 | 43.880–56.207 | 63.92 | equal | 12.87× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1053.392 | 1025.049–1234.116 | 65.95 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 100.229 | 91.228–135.246 | 63.28 | equal | 10.51× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 277.785 | 264.561–364.209 | 119.69 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 31.312 | 24.353–33.484 | 47.55 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.781 | 4.554–6.949 | 55.66 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 34.206 | 30.233–39.657 | 47.59 | reference | — | — | — |
| literal-type | 32 | candidate | 4.927 | 4.837–6.492 | 55.84 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 53.003 | 49.624–54.040 | 47.62 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.215 | 5.917–7.213 | 56.00 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.070 | 8.246–10.817 | 56.05 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 66.782 | 62.882–78.679 | 47.62 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 18.751 | 15.080–21.635 | 58.66 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 230.662 | 195.035–275.197 | 49.20 | reference | — | — | — |
| literal-type | 512 | python-reference | 290.874 | 267.879–407.735 | 49.48 | reference | — | — | — |
| literal-type | 512 | candidate | 21.375 | 19.828–27.592 | 58.89 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 353.519 | 335.619–487.062 | 51.39 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 34.737 | 31.847–50.471 | 61.92 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 508.862 | 496.950–529.456 | 51.95 | reference | — | — | — |
| literal-type | 1000 | candidate | 46.386 | 44.619–51.899 | 62.62 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.10, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
