# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-18T12:31:24.255134+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `c5c828aa2d37e30f85d97d54815454e8e0baee66`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 19.144 | 15.126–26.630 | 57.98 | equal | 10.11× | — | — |
| pipeline_rdfs | 100 | python-reference | 193.631 | 180.630–267.192 | 59.25 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 60.890 | 42.440–78.991 | 54.70 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 54.093 | 44.028–58.043 | 58.61 | equal | 8.77× | — | — |
| pipeline_owlrl | 100 | python-reference | 474.156 | 453.079–604.156 | 59.47 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 97.940 | 65.104–127.134 | 56.91 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 570.814 | 409.174–724.900 | 110.30 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1771.979 | 1707.176–2316.052 | 64.73 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 118.624 | 99.272–194.595 | 63.64 | equal | 14.94× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1483.481 | 1120.227–2380.225 | 65.73 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 103.577 | 92.624–135.791 | 63.16 | equal | 14.32× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 283.145 | 267.769–349.056 | 119.84 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 31.822 | 24.919–42.023 | 47.47 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 6.101 | 4.116–8.838 | 55.86 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 29.719 | 27.376–74.707 | 47.47 | reference | — | — | — |
| literal-type | 32 | candidate | 7.245 | 5.746–8.221 | 55.89 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 61.455 | 53.725–72.155 | 47.48 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.843 | 7.946–20.033 | 56.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.770 | 8.449–14.054 | 56.23 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 82.724 | 77.303–116.058 | 47.53 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 18.039 | 17.883–23.209 | 58.88 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 368.271 | 304.135–491.046 | 49.14 | reference | — | — | — |
| literal-type | 512 | python-reference | 310.531 | 242.129–685.486 | 49.47 | reference | — | — | — |
| literal-type | 512 | candidate | 51.530 | 48.807–73.737 | 59.11 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 1047.066 | 745.521–1204.693 | 51.33 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 77.758 | 70.157–95.215 | 62.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 1431.054 | 1352.913–1872.596 | 51.97 | reference | — | — | — |
| literal-type | 1000 | candidate | 105.742 | 100.358–135.929 | 62.75 | different | — | logical_inplace_owlrl_different | — |
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
