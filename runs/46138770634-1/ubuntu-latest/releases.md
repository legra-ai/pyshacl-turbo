# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T11:26:18.650442+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `f60a5103dc2e7d4e418741e6ad869bad37ff4df0`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 5.997 | 5.788–6.275 | 76.67 | equal | 8.70× | — | — |
| pipeline_rdfs | 100 | python-reference | 52.183 | 51.397–53.979 | 55.64 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 18.038 | 16.771–21.072 | 54.10 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.569 | 15.167–15.817 | 77.36 | equal | 8.04× | — | — |
| pipeline_owlrl | 100 | python-reference | 125.110 | 123.936–129.372 | 55.89 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 29.406 | 27.247–37.789 | 54.11 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 206.278 | 191.291–345.282 | 82.29 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 593.750 | 579.034–729.825 | 61.08 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 48.282 | 46.499–53.467 | 80.72 | equal | 12.30× | — | — |
| pipeline_owlrl | 1000 | python-reference | 926.564 | 903.363–1059.117 | 62.22 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 104.128 | 100.280–105.918 | 81.24 | equal | 8.90× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 292.779 | 259.727–370.944 | 88.86 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 18.852 | 18.644–19.454 | 52.48 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.630 | 3.544–3.775 | 74.45 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 21.508 | 21.095–27.178 | 86.36 | reference | — | — | — |
| literal-type | 32 | candidate | 4.195 | 4.080–4.330 | 95.86 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 47.247 | 46.117–47.806 | 120.73 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.755 | 6.426–7.122 | 120.73 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.116 | 7.986–11.650 | 229.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 58.821 | 58.315–75.038 | 229.17 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.842 | 16.570–21.014 | 340.31 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 160.362 | 157.454–215.761 | 340.31 | reference | — | — | — |
| literal-type | 512 | python-reference | 209.512 | 200.605–255.428 | 656.48 | reference | — | — | — |
| literal-type | 512 | candidate | 22.780 | 21.911–23.617 | 656.48 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 315.356 | 303.559–428.199 | 1064.62 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 29.648 | 28.914–30.719 | 1064.62 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 385.554 | 379.562–424.066 | 1660.16 | reference | — | — | — |
| literal-type | 1000 | candidate | 42.166 | 40.277–43.845 | 1660.16 | different | — | logical_inplace_owlrl_different | — |
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
