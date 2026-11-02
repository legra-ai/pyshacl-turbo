# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-02T12:49:36.577337+00:00; platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39.
Harness revision: `9d5910e6b6b2e011859a8b3b8a5b7251cb5d4d5b`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 13.775 | 13.552–13.840 | 64.46 | equal | 8.31× | — | — |
| pipeline_rdfs | 100 | python-reference | 114.433 | 113.593–115.017 | 47.38 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 31.488 | 30.989–37.858 | 44.30 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.990 | 23.866–24.260 | 65.41 | equal | 11.59× | — | — |
| pipeline_owlrl | 100 | python-reference | 277.977 | 276.458–284.207 | 47.70 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 46.670 | 46.410–51.842 | 45.47 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 325.586 | 317.359–452.020 | 73.90 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1165.142 | 1156.429–1262.364 | 52.89 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 115.702 | 112.120–119.113 | 70.04 | equal | 10.07× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1940.865 | 1920.927–2073.012 | 53.89 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 168.702 | 160.233–246.037 | 70.40 | equal | 11.50× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 441.995 | 436.085–550.251 | 80.41 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 4607.603 | 4506.230–4788.687 | 392.75 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 27847.213 | 27680.121–28552.524 | 118.39 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 1448.155 | 1399.084–1482.561 | 117.12 | equal | 19.23× | — | — |
| pipeline_owlrl | 10000 | python-reference | 18845.627 | 18736.695–19099.486 | 126.49 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1887.457 | 1828.726–2309.064 | 111.32 | equal | 9.98× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 6320.741 | 6221.272–6407.607 | 450.53 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 41.541 | 41.094–42.758 | 152.50 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.572 | 5.513–5.912 | 152.50 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 6.264 | 6.200–6.344 | 185.26 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 47.762 | 47.497–48.531 | 185.26 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 9.654 | 9.532–11.711 | 223.90 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 100.071 | 99.392–101.053 | 223.90 | reference | — | — | — |
| literal-type | 128 | python-reference | 128.211 | 125.668–130.862 | 313.67 | reference | — | — | — |
| literal-type | 128 | candidate | 11.944 | 11.665–12.606 | 313.67 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 341.155 | 336.103–383.719 | 424.37 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 26.269 | 25.335–26.730 | 424.37 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 444.431 | 438.297–496.409 | 741.59 | reference | — | — | — |
| literal-type | 512 | candidate | 35.377 | 34.767–35.992 | 741.59 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 47.553 | 46.516–49.950 | 1149.90 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 660.303 | 648.029–757.831 | 1149.90 | reference | — | — | — |
| literal-type | 1000 | candidate | 65.354 | 64.700–67.176 | 1748.80 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 851.790 | 839.359–873.992 | 1748.80 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.5, rdflib-turbo 0.2.0a27

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
