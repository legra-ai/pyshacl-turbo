# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-18T11:59:10.559944+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `c5c828aa2d37e30f85d97d54815454e8e0baee66`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.314 | 7.919–11.289 | 58.16 | equal | 7.38× | — | — |
| pipeline_rdfs | 100 | python-reference | 61.390 | 60.029–64.749 | 59.42 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 24.851 | 22.653–42.058 | 54.78 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.721 | 17.731–47.918 | 58.72 | equal | 6.33× | — | — |
| pipeline_owlrl | 100 | python-reference | 150.262 | 149.434–152.079 | 59.73 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 32.330 | 30.301–34.233 | 57.08 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 210.277 | 192.399–277.899 | 110.94 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 680.948 | 640.363–781.503 | 65.00 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 57.037 | 50.620–84.564 | 63.75 | equal | 11.94× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1136.782 | 1087.422–1300.528 | 66.03 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 136.620 | 121.312–147.360 | 63.14 | equal | 8.32× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 367.535 | 301.601–490.420 | 120.27 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 36.359 | 25.709–43.586 | 47.61 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.802 | 4.513–7.900 | 55.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 46.686 | 36.699–52.769 | 47.64 | reference | — | — | — |
| literal-type | 32 | candidate | 7.455 | 5.948–9.301 | 56.00 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 71.287 | 67.691–82.697 | 47.67 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 13.492 | 10.144–30.973 | 56.27 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.126 | 9.316–15.104 | 56.34 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 97.263 | 88.128–111.329 | 47.67 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.347 | 18.406–25.489 | 58.80 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 223.294 | 192.774–288.042 | 49.25 | reference | — | — | — |
| literal-type | 512 | python-reference | 256.603 | 242.641–294.291 | 49.58 | reference | — | — | — |
| literal-type | 512 | candidate | 25.578 | 22.099–36.493 | 59.19 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 386.151 | 358.239–509.716 | 51.50 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 37.046 | 29.064–46.179 | 62.03 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 480.760 | 434.163–494.514 | 52.05 | reference | — | — | — |
| literal-type | 1000 | candidate | 54.773 | 47.051–66.349 | 62.66 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
