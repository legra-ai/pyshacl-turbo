# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-02T16:52:08.762352+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `1fbe159029984365ffc705388cc1e2b33280c415`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 10.826 | 10.701–11.062 | 66.30 | equal | 8.65× | — | — |
| pipeline_rdfs | 100 | python-reference | 93.611 | 93.308–95.604 | 47.31 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 25.550 | 25.112–29.925 | 44.38 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.918 | 18.660–19.405 | 66.75 | equal | 12.21× | — | — |
| pipeline_owlrl | 100 | python-reference | 230.973 | 230.157–235.088 | 47.63 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 38.582 | 37.246–41.647 | 45.38 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 262.569 | 247.291–368.056 | 74.05 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 953.002 | 936.046–1019.500 | 52.84 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 84.564 | 82.731–85.947 | 72.01 | equal | 11.27× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1577.730 | 1566.562–1715.864 | 54.00 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 118.777 | 114.990–244.941 | 71.79 | equal | 13.28× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 362.023 | 337.960–424.510 | 80.32 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 34.779 | 34.472–36.274 | 42.76 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.393 | 4.307–4.549 | 64.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 40.059 | 39.741–40.187 | 76.76 | reference | — | — | — |
| literal-type | 32 | candidate | 5.019 | 4.899–5.143 | 86.26 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 86.393 | 85.718–86.742 | 110.89 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 7.679 | 7.589–7.784 | 110.89 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.349 | 9.203–9.577 | 219.02 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 106.925 | 105.816–108.001 | 219.02 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 20.005 | 19.533–20.254 | 330.34 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 296.422 | 292.536–322.135 | 330.34 | reference | — | — | — |
| literal-type | 512 | python-reference | 373.703 | 370.112–409.145 | 646.80 | reference | — | — | — |
| literal-type | 512 | candidate | 27.032 | 26.471–27.258 | 646.80 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 555.127 | 544.959–665.763 | 1055.10 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 36.059 | 35.592–37.146 | 1055.10 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 705.979 | 697.193–728.216 | 1650.14 | reference | — | — | — |
| literal-type | 1000 | candidate | 50.132 | 49.047–51.376 | 1650.14 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.8.0, rdflib-turbo 0.2.0a30

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
