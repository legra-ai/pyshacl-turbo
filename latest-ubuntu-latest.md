# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-26T14:10:17.301166+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 5.570 | 5.364–5.691 | 77.17 | equal | 8.97× | — | — |
| pipeline_rdfs | 100 | python-reference | 49.936 | 49.496–53.166 | 55.70 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 15.721 | 14.718–19.707 | 54.28 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 13.952 | 13.809–17.276 | 77.95 | equal | 8.70× | — | — |
| pipeline_owlrl | 100 | python-reference | 121.337 | 119.258–123.793 | 55.96 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 23.504 | 23.163–25.785 | 54.30 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 158.216 | 150.718–248.439 | 82.22 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 515.989 | 491.751–593.537 | 61.16 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 42.324 | 40.227–43.011 | 81.11 | equal | 12.19× | — | — |
| pipeline_owlrl | 1000 | python-reference | 835.243 | 796.404–949.944 | 62.22 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 92.057 | 90.570–96.563 | 81.93 | equal | 9.07× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 210.366 | 202.540–281.525 | 88.51 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 2675.712 | 2543.806–2804.930 | 400.26 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 13269.639 | 13182.236–13495.721 | 126.56 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 495.447 | 475.372–905.469 | 124.15 | equal | 26.78× | — | — |
| pipeline_owlrl | 10000 | python-reference | 8593.451 | 8358.920–8683.065 | 134.62 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1028.696 | 1006.825–1386.180 | 125.61 | equal | 8.35× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 4210.367 | 3930.732–4349.151 | 458.86 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 17.785 | 17.492–18.085 | 169.27 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.247 | 3.153–3.270 | 169.27 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 3.859 | 3.787–4.084 | 202.14 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 20.073 | 19.700–20.774 | 202.14 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 5.678 | 5.545–8.816 | 240.82 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 43.857 | 43.589–45.165 | 240.82 | reference | — | — | — |
| literal-type | 128 | python-reference | 55.458 | 54.604–60.924 | 329.57 | reference | — | — | — |
| literal-type | 128 | candidate | 7.355 | 6.968–7.772 | 329.57 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 147.236 | 143.081–189.112 | 440.21 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.069 | 15.571–16.906 | 440.21 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 189.089 | 188.099–226.454 | 753.34 | reference | — | — | — |
| literal-type | 512 | candidate | 21.095 | 20.437–21.342 | 753.34 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 27.627 | 27.204–28.155 | 1159.27 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 268.243 | 263.973–367.805 | 1159.27 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.826 | 38.158–39.455 | 1753.56 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 371.655 | 364.447–378.561 | 1753.56 | reference | — | — | — |
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
