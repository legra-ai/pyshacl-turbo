# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T08:46:00.736528+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `9aa243c37b1ff06d6481b38f55f0b6bb29e09306`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 12.271 | 10.430–16.237 | 59.11 | equal | 5.35× | — | — |
| pipeline_rdfs | 100 | python-reference | 65.636 | 63.495–73.985 | 60.69 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.910 | 17.837–24.946 | 55.84 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 17.758 | 17.310–18.665 | 59.56 | equal | 8.16× | — | — |
| pipeline_owlrl | 100 | python-reference | 144.963 | 135.231–155.796 | 60.95 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 27.345 | 26.141–28.609 | 58.16 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 203.105 | 161.982–332.347 | 110.34 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 609.559 | 553.646–739.461 | 66.20 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 80.277 | 65.240–106.170 | 65.81 | equal | 7.59× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1093.770 | 953.929–1233.004 | 67.33 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 97.529 | 90.586–99.223 | 64.11 | equal | 11.21× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 270.681 | 249.179–316.375 | 119.86 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 23.687 | 21.261–25.270 | 48.95 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.479 | 4.063–4.567 | 56.84 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.237 | 23.636–30.417 | 48.95 | reference | — | — | — |
| literal-type | 32 | candidate | 4.746 | 4.729–5.972 | 56.88 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 52.665 | 50.405–56.028 | 49.00 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.422 | 7.033–8.314 | 57.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 11.930 | 10.416–14.457 | 57.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 63.824 | 63.283–70.195 | 48.97 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.813 | 19.664–21.197 | 59.81 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 188.608 | 177.603–208.499 | 50.59 | reference | — | — | — |
| literal-type | 512 | python-reference | 236.632 | 218.989–271.233 | 50.89 | reference | — | — | — |
| literal-type | 512 | candidate | 23.577 | 22.601–29.916 | 60.09 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 378.866 | 347.894–461.798 | 52.83 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 30.619 | 30.286–33.783 | 62.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 420.732 | 416.703–449.429 | 53.34 | reference | — | — | — |
| literal-type | 1000 | candidate | 46.592 | 45.782–52.148 | 63.58 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.0, rdflib-turbo 0.2.0a20

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
