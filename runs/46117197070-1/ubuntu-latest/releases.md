# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T07:13:28.829143+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `c8489fac8dde19eb02c26b6d5d27dc5c29265c66`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.691 | 7.492–7.800 | 76.66 | equal | 8.87× | — | — |
| pipeline_rdfs | 100 | python-reference | 68.209 | 67.680–81.247 | 55.71 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 21.109 | 20.887–25.231 | 54.15 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 16.171 | 16.022–16.347 | 77.39 | equal | 10.03× | — | — |
| pipeline_owlrl | 100 | python-reference | 162.276 | 161.450–164.749 | 55.94 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 33.675 | 32.840–36.470 | 54.20 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 219.151 | 210.766–318.272 | 82.48 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 718.057 | 705.491–797.422 | 61.21 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 54.669 | 53.294–57.357 | 80.82 | equal | 13.13× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1130.824 | 1111.124–1244.734 | 62.16 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 103.012 | 101.378–103.816 | 81.18 | equal | 10.98× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 288.174 | 284.839–359.018 | 88.86 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 24.125 | 23.983–24.406 | 52.46 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.035 | 3.976–4.127 | 74.48 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 27.990 | 27.761–28.660 | 86.34 | reference | — | — | — |
| literal-type | 32 | candidate | 4.470 | 4.407–4.496 | 95.96 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 59.498 | 58.894–61.049 | 120.71 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.599 | 6.527–6.701 | 120.71 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 8.153 | 8.116–8.314 | 229.12 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 74.725 | 74.360–75.000 | 229.12 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 17.207 | 17.116–17.688 | 340.42 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 201.183 | 200.495–233.178 | 340.42 | reference | — | — | — |
| literal-type | 512 | python-reference | 258.905 | 254.586–300.150 | 656.55 | reference | — | — | — |
| literal-type | 512 | candidate | 23.343 | 23.193–23.649 | 656.55 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 386.014 | 379.568–471.335 | 1064.72 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 32.026 | 31.402–32.775 | 1064.72 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 503.434 | 496.344–511.134 | 1660.34 | reference | — | — | — |
| literal-type | 1000 | candidate | 43.209 | 43.060–43.649 | 1660.34 | different | — | logical_inplace_owlrl_different | — |
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
