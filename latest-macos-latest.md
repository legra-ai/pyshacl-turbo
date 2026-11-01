# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-01T11:13:51.863681+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `e5164a97129fa57013b0359b374bebecd333368b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.190 | 7.995–13.253 | 59.27 | equal | 5.73× | — | — |
| pipeline_rdfs | 100 | python-reference | 52.631 | 52.098–54.487 | 60.84 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 16.939 | 16.735–19.139 | 55.92 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 14.908 | 14.791–15.079 | 59.75 | equal | 8.52× | — | — |
| pipeline_owlrl | 100 | python-reference | 127.061 | 124.961–128.789 | 61.09 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 26.518 | 25.929–27.975 | 58.14 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 162.003 | 157.281–214.170 | 110.80 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 545.431 | 540.800–595.043 | 66.25 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 61.316 | 60.986–70.610 | 66.03 | equal | 8.90× | — | — |
| pipeline_owlrl | 1000 | python-reference | 876.492 | 870.867–925.566 | 67.50 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 86.800 | 86.592–88.229 | 64.38 | equal | 10.10× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 213.723 | 211.104–251.644 | 120.84 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 19.042 | 18.888–19.473 | 49.11 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.783 | 3.715–3.817 | 57.14 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.147 | 21.931–22.416 | 48.83 | reference | — | — | — |
| literal-type | 32 | candidate | 4.261 | 4.205–4.554 | 57.11 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 46.514 | 46.400–47.296 | 48.86 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.348 | 6.273–6.574 | 57.38 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 7.764 | 7.695–8.093 | 57.48 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 57.449 | 56.689–64.144 | 48.94 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 16.163 | 16.149–16.299 | 59.94 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 155.237 | 152.921–180.440 | 50.52 | reference | — | — | — |
| literal-type | 512 | python-reference | 201.304 | 199.614–224.614 | 50.81 | reference | — | — | — |
| literal-type | 512 | candidate | 21.618 | 21.561–21.738 | 60.14 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 295.579 | 294.349–341.929 | 52.92 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 28.653 | 28.215–28.842 | 63.23 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 405.086 | 402.658–407.881 | 53.53 | reference | — | — | — |
| literal-type | 1000 | candidate | 41.899 | 39.162–89.801 | 63.73 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.4, rdflib-turbo 0.2.0a24

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
