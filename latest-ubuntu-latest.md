# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-08T11:38:31.891629+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `ae8e55f7ecd688d7a1fafa4a73e42c8aab2fba43`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.542 | 9.312–9.730 | 68.87 | equal | 13.57× | — | — |
| pipeline_rdfs | 100 | python-reference | 129.471 | 128.882–131.512 | 48.59 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 32.100 | 31.707–37.436 | 46.84 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 22.461 | 21.992–23.834 | 69.32 | equal | 13.44× | — | — |
| pipeline_owlrl | 100 | python-reference | 301.825 | 299.669–306.611 | 48.83 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 47.360 | 46.566–51.581 | 46.91 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 319.394 | 310.107–413.652 | 75.07 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1258.550 | 1239.255–1329.899 | 53.33 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 67.281 | 67.053–69.599 | 72.01 | equal | 18.71× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2096.745 | 2082.589–2205.198 | 54.68 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 139.497 | 139.158–141.112 | 72.63 | equal | 15.03× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 415.800 | 405.266–483.370 | 81.46 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 4150.031 | 4061.242–4288.916 | 393.37 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 27640.697 | 27501.330–27809.499 | 119.41 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 758.324 | 738.161–1210.928 | 116.03 | equal | 36.45× | — | — |
| pipeline_owlrl | 10000 | python-reference | 20779.328 | 20615.203–20894.082 | 127.98 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1531.426 | 1495.708–1937.301 | 116.96 | equal | 13.57× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5752.919 | 5680.628–5901.454 | 451.94 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 46.489 | 46.251–46.856 | 154.20 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.212 | 5.115–5.305 | 154.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 6.013 | 5.944–6.078 | 187.00 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 54.138 | 53.775–54.621 | 187.00 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.083 | 9.032–9.260 | 225.70 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 114.601 | 113.545–118.329 | 225.70 | reference | — | — | — |
| literal-type | 128 | python-reference | 142.448 | 140.898–143.872 | 314.28 | reference | — | — | — |
| literal-type | 128 | candidate | 10.955 | 10.862–12.471 | 314.28 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 374.952 | 372.151–404.759 | 424.94 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 23.628 | 23.502–24.169 | 424.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 487.467 | 480.738–523.196 | 742.66 | reference | — | — | — |
| literal-type | 512 | candidate | 32.027 | 31.840–32.683 | 742.66 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 42.883 | 42.110–43.213 | 1151.07 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 712.858 | 703.043–778.591 | 1151.07 | reference | — | — | — |
| literal-type | 1000 | candidate | 59.158 | 58.745–59.568 | 1749.99 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 948.032 | 938.901–955.765 | 1749.99 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.10.0, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
