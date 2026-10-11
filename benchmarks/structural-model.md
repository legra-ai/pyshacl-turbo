# Shared structural-model compiler performance

Measured on 2026-10-11 with release builds, Python 3.13.16, pySHACL 0.40.1 and RDFLib 7.6.0. The baseline is `9cb81e829bd05fec65e52d01f66ea861a030415e`; the candidate is the integration working tree using the published `shacl-structural-model 3.0.0`. The JSON files record every source-file hash and the actual loaded native-module hash. Their `source_head` is the pre-commit base; the candidate source hashes identify its uncommitted changes.

Other-workspace Rust, Node and Python processes were active. This task ran no builds or tests alongside timings. These are descriptive measurements on a shared developer machine, with visible scheduling variation; small differences are not precise regression bounds. Every timed workload first passed full validation-report equivalence against pySHACL. The private screenshot workload is not included.

## Alternating compilation diagnostic

The initial broad run had a noisy compilation phase, so a separate diagnostic alternated old/new package order over four rounds in fresh subprocesses. Each round warmed both compilation paths, then interleaved seven samples per path. Process startup, fixture creation and the correctness gate are excluded. The same native binaries were used in both experiments. Each variant has 28 samples per phase.

The workload has 1,000 node shapes, each with one property shape, and 1,000 data nodes. Native compilation starts from an already serialized shapes document. The Python API includes RDFLib-to-document conversion. Both include parsing, structural reading, query/regex preparation and construction of the compiled program.

| Compilation path | Before ms | After ms | Change |
|---|---:|---:|---:|
| Native compiler | 81.84 | 82.74 | +1.1% |
| Python compile API | 104.55 | 104.89 | +0.3% |

Raw samples and subprocess order: [structural-compile-paired.json](structural-compile-paired.json). The larger initial compilation spike did not recur in this alternating diagnostic. The new model is consumed during compilation; reused validation executes the same native structures.

## Full validation with RDFLib input

Seven warmed, interleaved samples per backend; medians below include data conversion and report construction. Fresh Turbo includes shape compilation. Reuse excludes compilation. All shape-count rows use 1,000 data nodes; each node shape has one attached property shape and one explicit target.

| Workload | pySHACL after ms | Turbo before ms | Turbo after ms | Change | Turbo reuse after ms |
|---|---:|---:|---:|---:|---:|
| Core, 1,000 nodes | 49.05 | 29.63 | 29.68 | +0.2% | 29.04 |
| 10 node shapes | 1.21 | 13.89 | 14.65 | +5.4% | 13.04 |
| 100 node shapes | 8.69 | 24.42 | 24.08 | -1.4% | 13.59 |
| 1,000 node shapes | 89.87 | 133.90 | 136.28 | +1.8% | 25.73 |
| SPARQL rules, 100 nodes | 133.88 | 4.41 | 5.42 | +23.0% | 6.64 |

The Core reference median itself changed from 37.91 to 49.05 ms between runs. The rule reuse path was slower than fresh compilation in the second run, another sign of scheduling noise. Sparse targets remain expensive with fresh RDFLib data because conversion touches the entire input graph. These figures do not establish a general speedup over pySHACL.

## Existing PyOxigraph Store input

Initial Store loading is excluded. Native snapshot transfer, compilation, validation and RDFLib report construction are included.

| Workload | pySHACL after ms | Turbo before ms | Turbo after ms | Turbo reuse after ms |
|---|---:|---:|---:|---:|
| Core, 1,000 nodes | 354.88 | 20.13 | 20.50 | 19.97 |
| 10 node shapes | 3.48 | 6.87 | 7.00 | 5.84 |
| 100 node shapes | 30.41 | 17.16 | 17.36 | 6.68 |
| 1,000 node shapes | 306.72 | 127.79 | 126.99 | 17.78 |
| SPARQL rules, 100 nodes | 31.13 | 3.74 | 3.79 | 3.34 |

## Original broad-run compilation samples

These independent phase measurements are retained, including the noisy 1,000-shape result. Do not sum them with full-validation timings.

| Workload | Before ms | After ms |
|---|---:|---:|
| Core, 1,000 nodes | 0.279 | 0.309 |
| 10 node shapes | 1.174 | 1.220 |
| 100 node shapes | 9.801 | 9.805 |
| 1,000 node shapes | 105.268 | 141.528 |
| SPARQL rules, 100 nodes | 0.355 | 0.412 |

Full reports, raw samples and source hashes: [before](structural-before.json), [after](structural-after.json).

## Reproduce

Build both revisions with `maturin develop --release --locked` in separate environments/checkouts, or copy each built Python package including its native extension before rebuilding. Run each process with `PYTHONPATH` selecting that package and `--source-root` pointing to its matching source tree. The package-root arguments below contain the `pyshacl_turbo` directory.

```sh
PYTHONPATH=/path/to/before-package .venv/bin/python benchmarks/compiler.py --source-root /path/to/before-checkout --repeats 7 --load-note "Describe host load" --output benchmarks/structural-before.json
PYTHONPATH=/path/to/after-package .venv/bin/python benchmarks/compiler.py --source-root /path/to/after-checkout --repeats 7 --load-note "Describe host load" --output benchmarks/structural-after.json
.venv/bin/python benchmarks/compile_pair.py --baseline-package /path/to/before-package --candidate-package /path/to/after-package --output benchmarks/structural-compile-paired.json
```

The timing scripts fail if report parity fails. The paired script also verifies which native package each worker loaded. Compatibility remains a separate, incomplete measurement; these workloads do not establish 100% pySHACL compatibility.
