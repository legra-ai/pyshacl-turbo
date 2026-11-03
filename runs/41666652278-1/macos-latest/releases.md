# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-03T17:52:04.273798+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `8f03cd4296b36764950306219408eefd65624b28`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.842 | 6.703–10.776 | 59.53 | equal | 8.29× | — | — |
| pipeline_rdfs | 100 | python-reference | 65.047 | 58.482–74.754 | 60.83 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.139 | 19.702–24.449 | 55.89 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.439 | 18.753–27.047 | 60.05 | equal | 7.10× | — | — |
| pipeline_owlrl | 100 | python-reference | 145.113 | 138.212–169.843 | 61.08 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 28.509 | 26.607–32.390 | 58.06 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 178.212 | 169.904–245.680 | 111.12 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 738.356 | 674.907–782.256 | 66.33 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 70.326 | 59.090–97.207 | 65.12 | equal | 10.50× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1712.815 | 1328.640–1908.077 | 67.44 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 115.836 | 108.165–133.606 | 64.56 | equal | 14.79× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 276.914 | 229.102–358.387 | 121.08 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 23.643 | 19.739–26.577 | 49.11 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.744 | 4.243–8.352 | 57.19 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 26.433 | 26.176–28.869 | 49.11 | reference | — | — | — |
| literal-type | 32 | candidate | 5.109 | 4.802–8.992 | 57.19 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 50.840 | 47.573–74.120 | 49.09 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.810 | 6.989–10.278 | 57.48 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.362 | 8.246–13.048 | 57.56 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 72.348 | 69.814–88.452 | 49.19 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.704 | 18.527–23.549 | 60.05 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 199.106 | 179.354–336.100 | 50.62 | reference | — | — | — |
| literal-type | 512 | python-reference | 247.873 | 230.186–327.039 | 51.03 | reference | — | — | — |
| literal-type | 512 | candidate | 46.191 | 33.361–56.056 | 60.34 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 386.289 | 358.296–517.928 | 52.98 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 33.872 | 32.041–35.720 | 63.33 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 464.801 | 448.343–606.773 | 53.55 | reference | — | — | — |
| literal-type | 1000 | candidate | 50.654 | 47.415–58.980 | 63.83 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.9.1, rdflib-turbo 0.2.0a33

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
