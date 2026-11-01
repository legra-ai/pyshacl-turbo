# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-01T00:08:19.111598+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `a568c877783ff1b56f97275152191c5d38417149`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 11.202 | 10.990–11.343 | 65.71 | equal | 8.31× | — | — |
| pipeline_rdfs | 100 | python-reference | 93.142 | 92.213–94.749 | 47.41 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 26.728 | 26.099–31.513 | 44.46 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 19.202 | 18.838–19.326 | 66.64 | equal | 11.94× | — | — |
| pipeline_owlrl | 100 | python-reference | 229.332 | 228.024–233.241 | 47.57 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 39.241 | 38.837–42.417 | 45.67 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 258.393 | 251.723–363.605 | 74.03 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 940.747 | 930.956–1032.415 | 52.84 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 84.650 | 83.786–86.903 | 71.31 | equal | 11.11× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1609.166 | 1596.333–1750.420 | 53.84 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 115.204 | 113.766–238.467 | 70.56 | equal | 13.97× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 345.792 | 326.419–422.842 | 80.33 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 35.600 | 35.231–37.429 | 42.77 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.441 | 4.350–4.486 | 65.06 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 40.831 | 40.562–41.299 | 76.65 | reference | — | — | — |
| literal-type | 32 | candidate | 4.968 | 4.902–5.127 | 86.27 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 87.275 | 86.695–89.192 | 110.90 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.505 | 7.396–7.561 | 110.90 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.256 | 9.163–9.487 | 219.00 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 106.428 | 105.608–107.225 | 219.00 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 19.713 | 19.513–20.074 | 330.31 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 287.329 | 284.266–324.091 | 330.31 | reference | — | — | — |
| literal-type | 512 | python-reference | 374.470 | 373.589–413.563 | 646.90 | reference | — | — | — |
| literal-type | 512 | candidate | 26.841 | 26.563–27.507 | 646.90 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 539.203 | 533.999–646.661 | 1055.38 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 36.228 | 35.879–36.866 | 1055.38 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 728.067 | 722.499–737.844 | 1650.37 | reference | — | — | — |
| literal-type | 1000 | candidate | 50.198 | 48.921–51.706 | 1650.37 | different | — | logical_inplace_owlrl_different | — |
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
