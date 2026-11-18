# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-18T14:36:30.753907+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `e05b5b7519ce737be6d4cd51458cb0c71e59bcc2`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.869 | 7.538–7.911 | 76.60 | equal | 8.63× | — | — |
| pipeline_rdfs | 100 | python-reference | 67.908 | 67.599–73.274 | 55.63 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 22.022 | 21.800–27.171 | 54.23 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.402 | 16.190–16.753 | 77.35 | equal | 9.95× | — | — |
| pipeline_owlrl | 100 | python-reference | 163.188 | 162.322–165.002 | 55.94 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 34.318 | 32.750–37.720 | 54.20 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 225.150 | 219.629–316.992 | 82.41 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 729.364 | 716.203–849.303 | 61.19 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 55.291 | 54.428–57.102 | 80.62 | equal | 13.19× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1171.305 | 1147.972–1350.874 | 62.20 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 107.624 | 103.824–109.597 | 81.21 | equal | 10.88× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 315.118 | 310.159–403.083 | 88.95 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.330 | 24.113–24.784 | 52.45 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.285 | 4.270–4.368 | 74.40 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.990 | 27.784–28.662 | 86.33 | reference | — | — | — |
| literal-type | 32 | candidate | 4.748 | 4.682–4.812 | 95.95 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 60.116 | 59.910–61.531 | 120.70 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.516 | 6.899–9.781 | 120.70 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.488 | 8.378–8.962 | 228.76 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 75.215 | 74.801–76.097 | 228.76 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.720 | 17.562–17.888 | 339.93 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 203.918 | 200.165–251.861 | 339.93 | reference | — | — | — |
| literal-type | 512 | python-reference | 262.954 | 261.764–311.834 | 656.54 | reference | — | — | — |
| literal-type | 512 | candidate | 23.714 | 23.283–24.095 | 656.54 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 379.068 | 377.497–496.680 | 1064.80 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 31.611 | 31.536–32.697 | 1064.80 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 510.960 | 504.805–519.570 | 1659.70 | reference | — | — | — |
| literal-type | 1000 | candidate | 44.762 | 43.565–45.335 | 1659.70 | different | — | logical_inplace_owlrl_different | — |
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
