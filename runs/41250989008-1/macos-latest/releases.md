# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-01T00:08:39.926686+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `a568c877783ff1b56f97275152191c5d38417149`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.234 | 9.450–14.450 | 59.27 | equal | 5.54× | — | — |
| pipeline_rdfs | 100 | python-reference | 56.743 | 52.685–66.812 | 60.81 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 16.900 | 16.705–19.216 | 55.89 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 15.256 | 14.841–16.842 | 59.80 | equal | 8.54× | — | — |
| pipeline_owlrl | 100 | python-reference | 130.255 | 128.591–134.849 | 61.14 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 26.721 | 26.231–28.817 | 58.12 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 163.002 | 159.216–215.582 | 111.00 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 559.964 | 553.179–597.517 | 66.28 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 61.339 | 60.696–62.101 | 65.97 | equal | 9.13× | — | — |
| pipeline_owlrl | 1000 | python-reference | 907.783 | 880.595–1129.908 | 67.44 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 88.206 | 86.811–93.893 | 64.28 | equal | 10.29× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 223.410 | 218.051–264.190 | 120.80 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 19.091 | 18.907–19.544 | 49.12 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.848 | 3.803–3.943 | 57.03 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.244 | 21.793–22.333 | 49.17 | reference | — | — | — |
| literal-type | 32 | candidate | 4.263 | 4.221–4.299 | 57.12 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 47.527 | 45.993–50.643 | 49.17 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.301 | 7.114–7.582 | 57.38 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.845 | 7.743–9.058 | 57.44 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 58.740 | 57.497–60.313 | 49.16 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.623 | 16.379–21.143 | 60.02 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 161.502 | 157.682–181.566 | 50.73 | reference | — | — | — |
| literal-type | 512 | python-reference | 207.196 | 201.490–225.300 | 51.08 | reference | — | — | — |
| literal-type | 512 | candidate | 21.747 | 21.536–23.182 | 60.23 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 320.886 | 291.595–386.840 | 53.03 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 28.591 | 28.431–29.211 | 63.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 391.204 | 388.218–463.929 | 53.56 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.969 | 38.705–39.237 | 63.78 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.3, rdflib-turbo 0.2.0a24

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
