# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T09:00:34.175769+00:00; platform: Linux-7.0.0-1020-azure-x86_64-with-glibc2.43.
Harness revision: `985a797fe6b5b0372f267476bfbaf0ff367df8d6`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 9.358 | 9.051–14.151 | 76.75 | equal | 10.50× | — | — |
| pipeline_rdfs | 100 | python-reference | 98.248 | 97.542–100.951 | 55.73 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 28.781 | 28.473–34.061 | 53.91 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 20.787 | 20.463–21.206 | 77.38 | equal | 10.84× | — | — |
| pipeline_owlrl | 100 | python-reference | 225.358 | 223.235–228.243 | 55.89 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 44.218 | 42.699–61.591 | 54.10 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 281.739 | 269.645–368.486 | 82.52 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 1024.694 | 995.404–1101.436 | 61.18 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 65.860 | 65.315–68.146 | 80.71 | equal | 15.56× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1559.095 | 1531.555–1670.142 | 62.06 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 126.051 | 124.455–128.281 | 81.30 | equal | 12.37× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 378.545 | 368.211–468.495 | 88.73 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 32.723 | 32.394–33.264 | 52.54 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.043 | 4.934–5.957 | 74.50 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 37.314 | 37.283–37.775 | 86.42 | reference | — | — | — |
| literal-type | 32 | candidate | 5.515 | 5.466–5.677 | 96.04 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 83.316 | 82.828–85.103 | 120.79 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.271 | 8.183–8.404 | 120.79 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 9.929 | 9.908–10.098 | 229.27 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 100.312 | 99.462–101.610 | 229.27 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 21.227 | 21.008–25.221 | 340.40 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 268.061 | 266.899–300.070 | 340.40 | reference | — | — | — |
| literal-type | 512 | python-reference | 348.698 | 342.848–388.137 | 656.57 | reference | — | — | — |
| literal-type | 512 | candidate | 28.946 | 28.811–29.822 | 656.57 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 515.181 | 512.818–595.606 | 1064.94 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 38.637 | 38.447–40.172 | 1064.94 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 677.946 | 673.711–686.092 | 1660.53 | reference | — | — | — |
| literal-type | 1000 | candidate | 53.280 | 52.834–53.781 | 1660.53 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.9, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
