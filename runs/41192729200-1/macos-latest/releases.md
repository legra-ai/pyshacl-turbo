# Versioned shared-dataset pipeline benchmarks

Serial isolated wheel environments; parse → in-place inference → validation, including shape compilation and full public report output. Shapes are parsed before timing. Python uses the original three libraries; shared Turbo retains one native dataset; historical Turbo includes RDFLib conversion. One warmup precedes retained timing samples. Independent cold processes measure whole-process peak RSS before observation encoding. Full-output speedups require stable, completely equal outputs. Generalized RDF differences remain visible. No timing threshold on shared CI runners. Closed literal fanout profiles separately measure only the public in-place OWL-RL invocation through a call-local owner; capture setup/cleanup and all observation encoding are outside timers. Raw full-API comparison remains unchanged. A separate logical_inplace_owlrl result excludes only independently validated container/return route fields; complete raw namespace order, caches, effects and context still must match, with full raw warm/cold stability.

Measured: 2026-10-31T10:42:48.250570+00:00; platform: macOS-26.6.2-arm64-arm-64bit-Mach-O.
Harness revision: `9aa243c37b1ff06d6481b38f55f0b6bb29e09306`; dirty source tree: `False`. Candidate wheel source revisions and hashes are retained in the raw evidence.

| Operation/profile | Nodes | Environment | Median ms | Min–max ms | Peak MiB | Full-output parity | Speedup vs Python | Logical in-place OWL-RL status | Logical in-place ratio vs Python |
|---|---:|---|---:|---:|---:|---|---:|---|---:|
| pipeline_rdfs | 100 | candidate | 18.620 | 12.086–27.759 | 59.27 | equal | 5.25× | — | — |
| pipeline_rdfs | 100 | python-reference | 97.678 | 82.178–123.643 | 60.92 | reference | — | — | — |
| pipeline_rdfs | 100 | turbo-historical | 26.312 | 23.979–34.797 | 55.95 | different | — | — | — |
| pipeline_owlrl | 100 | candidate | 26.615 | 24.617–34.507 | 59.75 | equal | 9.09× | — | — |
| pipeline_owlrl | 100 | python-reference | 241.857 | 184.936–267.999 | 61.16 | reference | — | — | — |
| pipeline_owlrl | 100 | turbo-historical | 49.497 | 41.512–56.368 | 58.20 | different | — | — | — |
| pipeline_rdfs | 1000 | turbo-historical | 280.586 | 222.840–450.910 | 110.92 | different | — | — | — |
| pipeline_rdfs | 1000 | python-reference | 726.319 | 665.805–837.303 | 66.31 | reference | — | — | — |
| pipeline_rdfs | 1000 | candidate | 77.245 | 73.462–103.071 | 66.05 | equal | 9.40× | — | — |
| pipeline_owlrl | 1000 | python-reference | 1072.577 | 1004.084–1248.349 | 67.47 | reference | — | — | — |
| pipeline_owlrl | 1000 | candidate | 102.882 | 100.270–110.042 | 64.27 | equal | 10.43× | — | — |
| pipeline_owlrl | 1000 | turbo-historical | 241.747 | 232.347–311.195 | 121.09 | different | — | — | — |
| pipeline_rdfs | 10000 | turbo-historical | 3251.605 | 2801.724–3496.935 | 684.80 | different | — | — | — |
| pipeline_rdfs | 10000 | python-reference | 20392.573 | 16289.202–24745.714 | 142.03 | reference | — | — | — |
| pipeline_rdfs | 10000 | candidate | 894.618 | 844.369–999.284 | 142.58 | equal | 22.79× | — | — |
| pipeline_owlrl | 10000 | python-reference | 10903.218 | 10556.070–11098.652 | 151.12 | reference | — | — | — |
| pipeline_owlrl | 10000 | candidate | 1218.004 | 1142.820–1707.452 | 122.78 | equal | 8.95× | — | — |
| pipeline_owlrl | 10000 | turbo-historical | 4819.292 | 4704.151–5152.851 | 781.50 | different | — | — | — |
| literal-reflexivity | 32 | python-reference | 23.546 | 21.817–31.277 | 49.11 | reference | — | — | — |
| literal-reflexivity | 32 | candidate | 5.138 | 4.664–8.678 | 56.91 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | candidate | 5.207 | 5.028–5.331 | 56.98 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 32 | python-reference | 29.714 | 27.502–37.319 | 49.17 | reference | — | — | — |
| literal-reflexivity | 128 | candidate | 8.735 | 7.683–16.992 | 57.34 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 128 | python-reference | 77.842 | 59.480–83.366 | 49.22 | reference | — | — | — |
| literal-type | 128 | python-reference | 87.109 | 64.084–106.590 | 49.20 | reference | — | — | — |
| literal-type | 128 | candidate | 9.595 | 9.078–20.155 | 57.42 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 512 | python-reference | 232.558 | 187.586–306.343 | 50.73 | reference | — | — | — |
| literal-reflexivity | 512 | candidate | 22.900 | 18.704–28.749 | 59.86 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 512 | python-reference | 266.946 | 240.986–312.731 | 51.05 | reference | — | — | — |
| literal-type | 512 | candidate | 32.288 | 28.336–37.553 | 60.08 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | candidate | 40.774 | 31.829–51.793 | 63.03 | different | — | logical_inplace_owlrl_different | — |
| literal-reflexivity | 1000 | python-reference | 353.642 | 333.875–436.238 | 53.00 | reference | — | — | — |
| literal-type | 1000 | candidate | 49.910 | 45.882–63.852 | 63.62 | different | — | logical_inplace_owlrl_different | — |
| literal-type | 1000 | python-reference | 463.474 | 446.634–604.341 | 53.53 | reference | — | — | — |
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
- candidate: owlrl-turbo 0.2.0a1, pyshacl-turbo 0.7.0, rdflib-turbo 0.2.0a20

Raw observations, every timing/RSS sample, wheel/native hashes and dependency locks accompany this report.
Whole-process peak RSS includes imports and retained output. Small synthetic workloads do not establish universal speedups.
