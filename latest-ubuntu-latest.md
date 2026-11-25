# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-25T14:45:23.030428+00:00; platform: Linux-7.0.0-1016-aws-x86_64-with-glibc2.43.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.655 | 7.182–7.851 | 76.65 | equal | 9.27× | — | — |
| pipeline_rdfs | 100 | python-reference | 70.965 | 70.551–73.993 | 55.72 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.229 | 21.015–25.468 | 54.30 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.054 | 16.928–17.284 | 77.41 | equal | 9.79× | — | — |
| pipeline_owlrl | 100 | python-reference | 166.921 | 164.619–170.307 | 56.05 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 32.451 | 32.031–35.684 | 54.31 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 216.261 | 214.103–301.748 | 82.52 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 734.914 | 731.866–811.423 | 61.30 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 53.415 | 52.838–54.719 | 80.84 | equal | 13.76× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1167.937 | 1153.385–1279.730 | 62.29 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 110.330 | 108.597–112.801 | 81.47 | equal | 10.59× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 294.218 | 290.022–372.135 | 89.02 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3102.634 | 3043.113–3329.492 | 400.92 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 21220.606 | 21064.531–21826.701 | 126.39 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 602.329 | 564.694–902.723 | 124.06 | equal | 35.23× | — | — |
| pipeline_owlrl | 10000 | python-reference | 11786.221 | 11673.307–12010.985 | 135.24 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1317.623 | 1253.107–1607.881 | 124.95 | equal | 8.95× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 4518.651 | 4470.537–4810.692 | 459.87 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.532 | 23.765–24.679 | 169.64 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.048 | 3.984–4.246 | 169.64 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 4.656 | 4.560–4.963 | 202.54 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.952 | 27.426–28.979 | 202.54 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.090 | 6.704–7.325 | 241.24 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 61.225 | 60.655–62.922 | 241.24 | reference | — | — | — |
| literal-type | 128 | python-reference | 73.353 | 72.673–73.955 | 329.88 | reference | — | — | — |
| literal-type | 128 | candidate | 8.623 | 8.465–8.797 | 329.88 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 203.307 | 202.367–242.620 | 440.52 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.712 | 17.380–17.910 | 440.52 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 262.820 | 259.190–298.998 | 753.82 | reference | — | — | — |
| literal-type | 512 | candidate | 23.987 | 23.582–24.481 | 753.82 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 33.035 | 32.601–33.178 | 1159.70 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 395.737 | 386.050–473.684 | 1159.70 | reference | — | — | — |
| literal-type | 1000 | candidate | 45.092 | 44.928–45.763 | 1753.99 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 538.159 | 531.825–543.312 | 1753.99 | reference | — | — | — |
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
