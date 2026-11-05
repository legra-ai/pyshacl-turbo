# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-05T12:45:23.601937+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `b36b227b1766aee5397e3ff30b3076741e5fefdf`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.384 | 9.314–9.926 | 66.20 | equal | 13.52× | — | — |
| pipeline_rdfs | 100 | python-reference | 126.835 | 124.210–130.505 | 47.34 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 32.711 | 32.238–37.264 | 44.28 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 22.894 | 22.469–23.197 | 66.76 | equal | 13.34× | — | — |
| pipeline_owlrl | 100 | python-reference | 305.514 | 302.665–309.376 | 47.57 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 49.630 | 48.550–53.624 | 45.38 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 327.238 | 315.691–416.341 | 74.10 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1262.708 | 1245.879–1320.768 | 52.94 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 68.175 | 66.889–69.443 | 71.23 | equal | 18.52× | — | — |
| pipeline_owlrl | 1000 | python-reference | 2138.705 | 2107.770–2211.980 | 53.96 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 139.143 | 137.731–241.262 | 70.82 | equal | 15.37× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 421.731 | 413.198–496.618 | 80.41 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 4223.838 | 4159.014–4404.704 | 392.62 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 27910.643 | 27854.673–28045.870 | 118.43 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 759.792 | 743.378–772.002 | 113.89 | equal | 36.73× | — | — |
| pipeline_owlrl | 10000 | python-reference | 20596.843 | 20435.355–20858.050 | 126.59 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1532.948 | 1488.802–1887.311 | 103.81 | equal | 13.44× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 5859.297 | 5804.174–5933.028 | 450.60 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 45.810 | 45.733–47.326 | 152.44 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.308 | 5.236–5.356 | 152.44 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 5.891 | 5.859–6.200 | 185.38 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 53.469 | 53.197–54.538 | 185.38 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.965 | 8.892–9.114 | 224.00 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 113.134 | 111.889–113.646 | 224.00 | reference | — | — | — |
| literal-type | 128 | python-reference | 139.289 | 138.193–140.386 | 312.76 | reference | — | — | — |
| literal-type | 128 | candidate | 11.134 | 10.965–11.322 | 312.76 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 381.253 | 377.925–413.462 | 438.51 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 23.992 | 23.555–24.217 | 438.51 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 489.287 | 482.643–522.940 | 750.58 | reference | — | — | — |
| literal-type | 512 | candidate | 32.167 | 31.759–32.519 | 750.58 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 43.003 | 42.505–43.961 | 1150.32 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 706.583 | 702.555–783.530 | 1150.32 | reference | — | — | — |
| literal-type | 1000 | candidate | 58.654 | 58.222–59.605 | 1748.97 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 930.856 | 923.602–941.991 | 1748.97 | reference | — | — | — |
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
