# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T07:19:17.203311+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `c8489fac8dde19eb02c26b6d5d27dc5c29265c66`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 11.753 | 7.714–15.981 | 58.11 | equal | 5.50× | — | — |
| pipeline_rdfs | 100 | python-reference | 64.695 | 61.233–72.918 | 59.38 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.054 | 19.074–24.802 | 54.78 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.543 | 16.473–27.619 | 58.64 | equal | 8.68× | — | — |
| pipeline_owlrl | 100 | python-reference | 152.288 | 147.119–164.043 | 59.69 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.961 | 29.469–40.357 | 56.94 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 214.400 | 188.023–262.779 | 110.34 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 758.194 | 702.362–956.147 | 64.80 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 70.483 | 51.219–76.171 | 63.64 | equal | 10.76× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1343.424 | 1113.146–1882.659 | 65.88 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 101.396 | 93.310–115.401 | 63.25 | equal | 13.25× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 291.457 | 267.180–353.060 | 117.52 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 22.213 | 21.701–23.292 | 47.56 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.921 | 3.764–4.906 | 55.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 42.465 | 33.556–53.149 | 47.55 | reference | — | — | — |
| literal-type | 32 | candidate | 5.005 | 4.414–6.117 | 55.94 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 58.952 | 53.484–69.172 | 47.75 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.645 | 7.002–9.208 | 56.22 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.002 | 7.478–10.120 | 56.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 67.261 | 66.890–77.431 | 47.75 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 29.132 | 19.148–38.319 | 58.75 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 202.222 | 186.628–354.714 | 49.19 | reference | — | — | — |
| literal-type | 512 | python-reference | 214.755 | 208.761–231.107 | 49.59 | reference | — | — | — |
| literal-type | 512 | candidate | 23.979 | 21.779–26.273 | 59.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 411.177 | 367.903–453.220 | 51.36 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 50.038 | 38.508–59.111 | 62.02 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 674.212 | 602.517–791.816 | 52.11 | reference | — | — | — |
| literal-type | 1000 | candidate | 48.752 | 42.385–68.821 | 62.58 | different | — | logical_inplace_owlrl_different | — |
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
