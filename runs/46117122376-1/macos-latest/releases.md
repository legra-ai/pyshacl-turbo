# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T06:48:32.700033+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `c8489fac8dde19eb02c26b6d5d27dc5c29265c66`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.432 | 6.022–8.467 | 58.06 | equal | 8.07× | — | — |
| pipeline_rdfs | 100 | python-reference | 59.990 | 54.965–65.012 | 59.38 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 18.525 | 16.807–25.392 | 54.66 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 19.524 | 14.584–20.363 | 58.62 | equal | 9.41× | — | — |
| pipeline_owlrl | 100 | python-reference | 183.774 | 157.270–197.958 | 59.61 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 35.988 | 29.229–43.323 | 56.91 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 209.122 | 186.392–315.634 | 110.03 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 673.767 | 581.309–942.524 | 64.78 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 46.765 | 43.041–61.904 | 63.80 | equal | 14.41× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1100.901 | 906.758–1196.038 | 65.98 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 101.774 | 93.837–116.242 | 62.95 | equal | 10.82× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 291.713 | 225.459–310.713 | 117.23 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 21.704 | 19.676–22.907 | 47.58 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.600 | 3.661–4.839 | 55.75 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 22.353 | 21.963–22.789 | 47.58 | reference | — | — | — |
| literal-type | 32 | candidate | 4.099 | 4.003–4.448 | 55.75 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 47.677 | 46.233–50.990 | 47.58 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.856 | 6.331–8.509 | 56.02 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 12.068 | 9.137–13.871 | 56.16 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 65.504 | 63.525–70.625 | 47.53 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 18.484 | 17.029–25.390 | 58.70 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 202.927 | 189.665–245.147 | 49.20 | reference | — | — | — |
| literal-type | 512 | python-reference | 245.871 | 232.118–347.400 | 49.44 | reference | — | — | — |
| literal-type | 512 | candidate | 26.353 | 22.614–30.162 | 58.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 416.167 | 350.930–538.550 | 51.44 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 30.765 | 29.190–36.468 | 62.00 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 483.525 | 457.389–520.035 | 52.00 | reference | — | — | — |
| literal-type | 1000 | candidate | 38.614 | 36.317–42.079 | 62.45 | different | — | logical_inplace_owlrl_different | — |
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
