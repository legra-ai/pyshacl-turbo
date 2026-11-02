# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-02T18:12:46.157263+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `1fbe159029984365ffc705388cc1e2b33280c415`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.435 | 8.659–11.686 | 59.58 | equal | 5.92× | — | — |
| pipeline_rdfs | 100 | python-reference | 55.839 | 54.538–70.559 | 60.75 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 18.288 | 17.972–22.201 | 55.84 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.050 | 16.617–20.886 | 60.05 | equal | 7.54× | — | — |
| pipeline_owlrl | 100 | python-reference | 136.023 | 133.037–139.638 | 61.12 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 29.892 | 27.208–33.322 | 58.12 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 182.137 | 166.984–238.162 | 110.42 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 648.687 | 578.630–734.480 | 66.34 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 68.871 | 65.099–82.841 | 66.14 | equal | 9.42× | — | — |
| pipeline_owlrl | 1000 | python-reference | 980.919 | 918.618–1072.167 | 67.48 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 93.478 | 91.733–96.107 | 64.47 | equal | 10.49× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 235.510 | 225.705–342.270 | 120.58 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 23.003 | 20.672–30.081 | 49.17 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.108 | 3.993–4.891 | 57.03 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.853 | 22.511–24.566 | 49.03 | reference | — | — | — |
| literal-type | 32 | candidate | 4.466 | 4.422–4.864 | 57.06 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 48.171 | 47.844–51.491 | 49.08 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.686 | 7.449–7.790 | 57.34 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.315 | 8.269–8.718 | 57.45 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 60.430 | 59.199–60.848 | 49.08 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.615 | 18.866–22.403 | 59.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 179.396 | 164.374–203.178 | 50.69 | reference | — | — | — |
| literal-type | 512 | python-reference | 214.116 | 211.556–239.561 | 50.89 | reference | — | — | — |
| literal-type | 512 | candidate | 23.776 | 22.735–26.719 | 60.28 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 311.582 | 308.097–387.633 | 52.86 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 32.586 | 29.965–33.616 | 63.22 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 410.898 | 404.078–458.036 | 53.47 | reference | — | — | — |
| literal-type | 1000 | candidate | 41.351 | 40.951–42.264 | 63.69 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.8.0, rdflib-turbo 0.2.0a30

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
