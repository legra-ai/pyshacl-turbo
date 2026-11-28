# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-11-28T12:28:51.586596+00:00; platform: macOS-26.7.2-arm64-arm-64bit-Mach-O.
Harness revision: `f60a5103dc2e7d4e418741e6ad869bad37ff4df0`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 7.421 | 7.242–11.364 | 58.11 | equal | 9.41× | — | — |
| pipeline_rdfs | 100 | python-reference | 69.863 | 64.152–82.107 | 59.33 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 20.812 | 19.474–23.299 | 54.59 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 18.828 | 17.115–20.490 | 58.61 | equal | 8.35× | — | — |
| pipeline_owlrl | 100 | python-reference | 157.162 | 147.651–179.582 | 59.67 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 35.332 | 31.836–46.881 | 56.84 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 221.807 | 189.103–275.053 | 110.02 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 693.174 | 654.309–904.715 | 64.84 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 51.466 | 46.724–58.642 | 63.64 | equal | 13.47× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1334.306 | 1053.107–1436.043 | 66.02 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 103.159 | 99.147–146.217 | 63.05 | equal | 12.93× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 380.146 | 299.626–677.066 | 119.88 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 26.222 | 23.683–28.860 | 47.48 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.051 | 4.852–5.874 | 55.80 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 33.043 | 28.894–36.336 | 47.64 | reference | — | — | — |
| literal-type | 32 | candidate | 5.085 | 4.863–5.333 | 55.81 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 75.966 | 69.718–86.475 | 47.50 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.896 | 7.770–11.286 | 56.20 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | candidate | 10.192 | 9.515–14.580 | 56.22 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 128 | python-reference | 73.904 | 70.610–76.935 | 47.66 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 18.467 | 17.088–20.659 | 58.69 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 199.616 | 188.458–253.002 | 49.28 | reference | — | — | — |
| literal-type | 512 | python-reference | 258.664 | 239.644–305.383 | 49.55 | reference | — | — | — |
| literal-type | 512 | candidate | 28.403 | 26.449–46.414 | 59.03 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 415.425 | 358.224–664.290 | 51.47 | reference | — | — | — |
| literal-reflexivity | 1000 | candidate | 32.813 | 30.555–36.984 | 62.09 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 527.985 | 464.290–625.979 | 52.05 | reference | — | — | — |
| literal-type | 1000 | candidate | 50.618 | 38.595–57.893 | 62.53 | different | — | logical_inplace_owlrl_different | — |
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
- candidate: owlrl-turbo 0.2.0a2, pyshacl-turbo 0.10.10, rdflib-turbo 0.2.0a43

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
