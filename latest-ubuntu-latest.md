# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-18T13:28:21.685270+00:00; platform: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43.
Harness revision: `c5c828aa2d37e30f85d97d54815454e8e0baee66`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.540 | 9.213–9.623 | 76.47 | equal | 10.20× | — | — |
| pipeline_rdfs | 100 | python-reference | 97.294 | 96.589–102.224 | 55.54 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 29.113 | 28.165–33.593 | 53.86 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.669 | 20.310–21.109 | 77.16 | equal | 10.84× | — | — |
| pipeline_owlrl | 100 | python-reference | 224.077 | 219.807–227.708 | 55.92 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 45.452 | 42.900–49.723 | 53.91 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 290.183 | 278.767–392.574 | 82.18 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1033.032 | 1004.530–1151.461 | 61.16 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 67.049 | 66.129–75.590 | 80.55 | equal | 15.41× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1545.686 | 1518.170–1662.535 | 62.23 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 127.229 | 124.499–129.503 | 81.28 | equal | 12.15× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 374.714 | 358.194–427.322 | 88.68 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3862.235 | 3652.423–4075.048 | 400.29 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 27991.035 | 27690.401–28233.258 | 126.59 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 838.934 | 820.659–867.515 | 123.82 | equal | 33.37× | — | — |
| pipeline_owlrl | 10000 | python-reference | 15625.868 | 15460.456–15686.880 | 135.17 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1490.376 | 1395.927–1937.829 | 124.78 | equal | 10.48× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5811.677 | 5746.870–5996.276 | 459.02 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.457 | 32.302–33.744 | 162.51 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.168 | 5.124–5.480 | 162.51 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 5.685 | 5.527–5.783 | 195.25 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 38.012 | 37.447–39.241 | 195.25 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.456 | 8.270–9.129 | 233.98 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 79.880 | 79.495–85.705 | 233.98 | reference | — | — | — |
| literal-type | 128 | python-reference | 100.653 | 98.777–100.909 | 322.69 | reference | — | — | — |
| literal-type | 128 | candidate | 10.557 | 10.432–10.675 | 322.69 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 272.878 | 267.055–309.237 | 433.38 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.785 | 21.525–22.988 | 433.38 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 351.698 | 350.577–389.693 | 751.09 | reference | — | — | — |
| literal-type | 512 | candidate | 29.547 | 29.108–30.128 | 751.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 38.985 | 38.516–39.971 | 1159.35 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 513.876 | 507.921–599.039 | 1159.35 | reference | — | — | — |
| literal-type | 1000 | candidate | 54.124 | 53.467–55.045 | 1758.33 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 674.174 | 670.478–688.705 | 1758.33 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
