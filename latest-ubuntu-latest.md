# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T06:50:43.997199+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `c8489fac8dde19eb02c26b6d5d27dc5c29265c66`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.351 | 9.204–16.432 | 76.70 | equal | 9.18× | — | — |
| pipeline_rdfs | 100 | python-reference | 95.062 | 94.774–98.210 | 55.61 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 28.293 | 27.860–34.405 | 54.23 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.277 | 19.928–20.933 | 77.12 | equal | 10.89× | — | — |
| pipeline_owlrl | 100 | python-reference | 220.849 | 219.850–230.884 | 55.89 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 42.913 | 42.473–47.191 | 54.24 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 276.149 | 266.961–362.641 | 82.43 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1009.662 | 1003.031–1100.585 | 61.15 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 65.849 | 64.662–68.778 | 80.84 | equal | 15.33× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1544.582 | 1536.258–1633.732 | 62.13 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 124.447 | 123.664–125.120 | 81.47 | equal | 12.41× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 364.653 | 357.229–432.044 | 88.73 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.335 | 32.029–32.955 | 52.27 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.900 | 4.786–4.935 | 74.32 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 37.648 | 37.214–39.008 | 86.14 | reference | — | — | — |
| literal-type | 32 | candidate | 5.462 | 5.335–5.510 | 95.77 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 80.152 | 79.469–81.371 | 120.52 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.206 | 8.072–8.471 | 120.52 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.999 | 9.798–10.155 | 229.10 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 99.325 | 99.157–100.883 | 229.10 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 20.942 | 20.835–21.633 | 340.26 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 268.685 | 266.157–298.279 | 340.26 | reference | — | — | — |
| literal-type | 512 | python-reference | 349.687 | 348.210–376.835 | 656.38 | reference | — | — | — |
| literal-type | 512 | candidate | 28.551 | 27.984–29.538 | 656.38 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 521.042 | 516.435–588.967 | 1064.62 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 37.885 | 37.253–38.386 | 1064.62 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 670.494 | 665.947–674.950 | 1660.12 | reference | — | — | — |
| literal-type | 1000 | candidate | 53.275 | 52.478–53.718 | 1660.12 | different | — | logical_inplace_owlrl_different | — |
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
