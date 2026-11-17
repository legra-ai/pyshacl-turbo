# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-17T18:39:14.104334+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `7f9683b8e9f9b501579e60cfd956f9386b4fb27d`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 5.086 | 4.897–7.124 | 58.12 | equal | 9.34× | — | — |
| pipeline_rdfs | 100 | python-reference | 47.500 | 46.776–56.025 | 59.27 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 15.129 | 14.890–17.369 | 54.39 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 11.993 | 11.773–12.158 | 58.58 | equal | 9.44× | — | — |
| pipeline_owlrl | 100 | python-reference | 113.171 | 112.901–128.641 | 59.52 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 24.696 | 23.357–25.353 | 56.64 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 151.800 | 143.585–196.425 | 107.38 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 493.492 | 483.247–558.572 | 64.70 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 37.225 | 36.707–37.670 | 63.77 | equal | 13.26× | — | — |
| pipeline_owlrl | 1000 | python-reference | 784.077 | 771.822–855.621 | 65.84 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 68.297 | 68.159–77.924 | 63.20 | equal | 11.48× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 193.750 | 192.518–228.489 | 116.48 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 16.930 | 16.828–17.029 | 47.52 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 3.148 | 3.122–3.552 | 55.91 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 19.519 | 19.255–19.692 | 47.52 | reference | — | — | — |
| literal-type | 32 | candidate | 3.509 | 3.473–3.532 | 55.92 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 40.772 | 40.413–41.480 | 47.58 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 5.399 | 5.303–6.133 | 56.23 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 6.197 | 6.144–6.561 | 56.17 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 51.240 | 50.893–51.860 | 47.56 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 12.591 | 12.551–12.822 | 58.69 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 141.484 | 138.587–156.469 | 49.19 | reference | — | — | — |
| literal-type | 512 | python-reference | 176.778 | 173.315–215.611 | 49.42 | reference | — | — | — |
| literal-type | 512 | candidate | 16.740 | 16.681–16.835 | 59.06 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 276.790 | 260.743–305.862 | 51.39 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 22.393 | 22.143–26.236 | 62.06 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 342.633 | 338.639–358.758 | 52.03 | reference | — | — | — |
| literal-type | 1000 | candidate | 30.113 | 30.017–30.237 | 62.53 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.2, rdflib-turbo 0.2.0a39

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
