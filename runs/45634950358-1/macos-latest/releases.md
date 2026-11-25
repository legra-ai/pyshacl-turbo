# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-25T14:54:57.075254+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `f0d8f379a7f3a9a388ea23bbb18d344e3daccc67`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 8.096 | 7.529–11.143 | 58.06 | equal | 10.27× | — | — |
| pipeline_rdfs | 100 | python-reference | 83.125 | 67.134–89.606 | 59.31 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 27.697 | 22.131–31.757 | 54.39 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 23.781 | 19.716–36.848 | 58.61 | equal | 7.00× | — | — |
| pipeline_owlrl | 100 | python-reference | 166.363 | 140.085–354.690 | 59.69 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 45.646 | 36.862–57.239 | 56.48 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 229.886 | 200.643–367.844 | 106.36 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 746.987 | 673.013–1121.772 | 64.80 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 46.596 | 44.986–49.031 | 63.94 | equal | 16.03× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1203.042 | 1043.618–1266.387 | 65.86 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 110.603 | 103.942–160.585 | 63.11 | equal | 10.88× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 447.776 | 362.471–535.996 | 115.89 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3435.697 | 3062.548–4449.834 | 643.23 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 26658.246 | 22326.295–27760.326 | 140.41 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 585.190 | 533.520–728.576 | 128.38 | equal | 45.55× | — | — |
| pipeline_owlrl | 10000 | python-reference | 11259.233 | 10417.818–14175.450 | 149.52 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1251.120 | 966.130–1872.154 | 121.23 | equal | 9.00× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 4610.312 | 4250.330–5262.756 | 737.12 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 22.708 | 21.536–23.590 | 47.69 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 4.548 | 4.384–5.878 | 55.88 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 5.027 | 4.531–5.099 | 55.89 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 26.964 | 25.135–27.936 | 47.66 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 6.907 | 6.271–7.404 | 56.12 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 71.612 | 63.136–80.732 | 47.73 | reference | — | — | — |
| literal-type | 128 | python-reference | 66.852 | 65.503–73.108 | 47.66 | reference | — | — | — |
| literal-type | 128 | candidate | 8.314 | 8.212–8.442 | 56.23 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 183.257 | 179.977–213.414 | 49.31 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 22.502 | 17.281–27.999 | 58.75 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 260.604 | 240.594–317.262 | 49.58 | reference | — | — | — |
| literal-type | 512 | candidate | 23.430 | 22.566–27.050 | 59.05 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 30.680 | 30.121–37.610 | 62.12 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 386.709 | 355.097–483.327 | 51.50 | reference | — | — | — |
| literal-type | 1000 | candidate | 44.216 | 40.946–53.168 | 62.62 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 480.607 | 449.007–581.729 | 52.05 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.4, rdflib-turbo 0.2.0a41

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
