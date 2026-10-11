# pyshacl-turbo

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![Rust](https://img.shields.io/badge/Rust-1.98%2B-DEA584?logo=rust&logoColor=black)](rust-toolchain.toml)
[![License: MIT OR Apache-2.0](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-blue)](LICENSE-MIT)
[![Python coverage measured by pytest-cov](https://legra-ai.github.io/pyshacl-turbo/coverage.svg)](https://legra-ai.github.io/pyshacl-turbo/)
[![pySHACL non-JS suite: 100% (403/403)](https://img.shields.io/badge/pySHACL%20non--JS%20suite-100%25-brightgreen)](docs/compatibility.md#measurements)

[![Tests and wheels](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/ci.yml)
[![Compatibility](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/compatibility.yml/badge.svg?branch=main)](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/compatibility.yml)
[![Regex](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/regex.yml/badge.svg?branch=main)](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/regex.yml)

A Rust SHACL engine with Python bindings. Shape compilation, Core
validation, SPARQL constraints, targets, rules and inference execute in Rust.
There is no runtime dependency on pySHACL or owlrl. Native execution releases
the Python GIL.

Compatibility work targets **pySHACL 0.40.1, excluding SHACL-JS**. It is incomplete.
The locally corrected upstream suite passes **403/403 cases (100%)**: 400
unchanged behavioral cases, one corrected fixture, and 2 explicitly recorded
native equivalents for Python implementation tests. The corrected fixture
checks that invalid geometry data is rejected and that supplying its missing
subclass relationship makes it valid. Both engines pass these assertions with
equivalent reports; see [the correction](vendor/pyshacl-issue-70.patch) and
[ADR 0018](docs/adr/0018-correct-upstream-geometry-fixture.md).
The pinned W3C suite passes **120/120 (100%) with document inputs** and
**119/120 with RDFLib Graph inputs**. The latter retains a documented
input-dependent pySHACL behavior. These are separate measurements;
see [compatibility](docs/compatibility.md) and the case-level
[upstream report](docs/upstream-coverage.json).

Core and SPARQL patterns execute Python-compatible regexes natively, including
lookarounds and backreferences. SPARQL REPLACE retains the pinned RDFLib
replacement behavior; native callbacks and query results preserve exact literal
terms. See [ADR 0015](docs/adr/0015-native-sparql-patterns.md) for the contract and
remaining regex limits.

Count and length bounds retain exact arbitrary-precision values, with pySHACL's
parameter-specific datatype rules. See [ADR 0016](docs/adr/0016-exact-integer-parameters.md)
for integer and qualified-count behavior.

## Build

Requires Rust/Cargo, Python 3.11+ and uv. Development uses Python 3.13.
The repository pins Rust 1.98.0 for compilation and formatting.

```sh
make dev
make check
```

## Python

```python
from pyshacl_turbo import compile_shapes, validate

conforms, report_graph, report_text = validate(
    "data.ttl", shacl_graph="shapes.ttl", advanced=True
)

# Compile once and reuse across independent datasets.
program = compile_shapes("shapes.ttl", advanced=True)
conforms, report_graph, report_text = program.validate("data.ttl")
```

Inputs include RDFLib Graph/Dataset objects, paths, URLs, file objects, RDF text
and bytes. Supported formats include Turtle, N-Triples, N-Quads, TriG, RDF/XML,
N3 and JSON-LD. Named graphs remain available to SPARQL GRAPH clauses; Core
validation sees their union. Reports are RDFLib graphs by default.

PyOxigraph Store input is also supported. Install the optional `oxigraph` extra
when PyOxigraph is not already installed:

```python
from pyoxigraph import RdfFormat, Store
from pyshacl_turbo import validate

store = Store()
store.load(path="data.trig", format=RdfFormat.TRIG)
conforms, report, text = validate(store, shacl_graph="shapes.ttl", advanced=True)
```

The Store input path avoids an intermediate RDFLib data graph. Independent
Python extensions exchange a native N-Quads snapshot, so it is **not zero-copy**.
See [Store input details](docs/store-inputs.md).
Named graphs and blank-node labels are preserved. Literal spellings already
normalized by a caller's Store cannot be recovered. Store rule and inference additions commit
atomically only with `inplace=True`, after successful execution. Only new quads
are committed; concurrent deletion of input quads is not undone.

RDFS and OWL-RL inference are implemented natively and selected with
`inference="rdfs"`, `"owlrl"` or `"both"`. Coverage is still being expanded;
current inferred graphs do not always match the reference's complete closure.
`owlrl` is installed only by the reference-test extra, not as a runtime backend.

## Rust

The standalone `pyshacl-turbo-engine` crate accepts exact-term oxrdf Dataset
values and `oxigraph::Store` inputs. `CompiledShapes::validate_store` and
`expand_store` copy a consistent quad snapshot without RDF text conversion.
Their `inplace` flag controls atomic addition of derived quads to the Store.
Compiled programs are shareable across threads; parallelism is caller-controlled.

Shape compilation uses [shacl-structural-model](https://github.com/legra-ai/shacl-structural-model)
with Turbo's exact RDF terms, then prepares native queries, regexes and indexes
for execution. The original graph remains available for reports and source
identity. See [ADR 0017](docs/adr/0017-shared-structural-compiler.md).

## Performance

```sh
make benchmark
```

The [compiler integration comparison](benchmarks/structural-model.md) records
before/after compilation and validation timings, including reused shapes, with
complete report parity required before timing.

The [performance report](benchmarks/current.md) compares RDFLib inputs and
already loaded PyOxigraph Stores, including conversion and report construction.
It includes shape reuse, increasing data and shape counts, SPARQL rules and
reasoning. Every timed path first has to produce an equivalent complete report.
Raw samples, versions and source hashes are in
[current.json](benchmarks/current.json). The original measurements are
preserved in [performance-baseline.json](benchmarks/performance-baseline.json).

Measurements are workload-specific. Sparse targeting can be slower because
Turbo must copy the input graph. Reasoning timings are provisional where the
complete inferred graphs differ, even when validation reports agree. Reference
backend errors are recorded without assigning a speedup.
The latest run was made while other workspace builds were active; its raw
samples show substantial scheduling variation. Sparse-target workloads remain
slower with fresh RDFLib input. See the report's load notes before using its
speedup ratios for capacity planning.

The [last full matrix](benchmarks/current.md) includes literal identity,
report graph context and inference axiom fixes. It predates the recursion and
undefined-function changes in ADR 0012; its recorded source hashes identify
the measured checkpoint. Earlier matrices remain in `benchmarks/`.
The [newer Core measurements](benchmarks/pattern-core.md) include the Python
pattern compatibility changes in ADR 0013, at 100, 1,000 and 10,000 nodes.
The [SPARQL pattern measurements](benchmarks/sparql-patterns.md) exercise native
REGEX and REPLACE at 100 and 1,000 nodes through both RDFLib and Store inputs.
The report records concurrent build load alongside the raw interleaved samples.
These measurements precede ADR 0016's integer-parameter changes; their source
hashes identify the measured implementation.

```sh
# Run alone, separately from builds and other tests.
.venv/bin/python benchmarks/check_core.py

# Full-report-gated SPARQL regex and replacement comparison.
.venv/bin/python benchmarks/matrix.py --kinds sparql-patterns --repeats 7 --output benchmarks/sparql-patterns.json

# Original SPARQL pipeline comparison, including both reference backends.
make benchmark-pipeline
```

## Verification and architecture

Local regressions compare full reports, rule output, graph mutation, blank-node
identity, namespace handling, Store inputs and errors. Pinned W3C and pySHACL
assets live under tests/w3c and vendor/pyshacl respectively.

```sh
make coverage
make test-compatibility
make test-regex
make test-sparql-evaluator
make test-coverage
.venv/bin/python scripts/run_upstream.py
.venv/bin/python scripts/run_upstream.py --reference
.venv/bin/python scripts/audit_reference_fixture.py
```

The three workflow badges report required CI checks on `main`. Each workflow also runs on
pull requests, daily, and on manual dispatch:

| Workflow | What it verifies |
| --- | --- |
| Tests and wheels | Python and Rust regressions, formatting and lint on Linux Python 3.11/3.13 and macOS Python 3.13; SPARQL evaluator tests with compatibility features disabled and enabled; source archive rebuilt into Linux x86-64/ARM64, macOS Intel/Apple Silicon, and Windows x86-64 wheels, installed with only runtime dependencies. The release also requires Compatibility and Regex at the same prepared revision. |
| Compatibility | All pinned W3C Core/SPARQL cases through both document and Graph APIs, the complete locally corrected non-JS pySHACL inventory, and the corrected geometry test with both engines and full report comparison. Case-level JSON and W3C JUnit XML are uploaded as artifacts. |
| Regex | The patched matcher's full upstream suite, unit tests with Turbo's base features, Python-mode VM regressions, and formatting, using its own pinned test dependencies. |

The [Python coverage report](https://legra-ai.github.io/pyshacl-turbo/) measures
the complete `pyshacl_turbo` Python package with `pytest-cov`, including uncovered
files and branches. CI requires **100% line and branch coverage**
on Linux Python 3.13. XML, JSON and HTML reports are uploaded for each run; passing
`main` runs publish the HTML report and measured percentage badge to GitHub Pages.
`make test-coverage` generates the same report locally in `htmlcov/`.
This measures Python API/CLI code coverage; it does not measure Rust code coverage
or SHACL compatibility. No package files are omitted from the denominator.

A green Compatibility badge means the documented baseline holds: **403/403**
locally corrected upstream passes, **120/120** W3C document passes and **119/120**
W3C Graph passes. Every upstream case must pass; the one local fixture correction
and two native equivalents remain identified in the report. The corrected
fixture must also pass its independent two-engine audit. The W3C Graph divergence
remains a strict expected failure. New failures and unexpected Graph passes fail
CI. These badges do not claim complete pySHACL compatibility.

Upstream allowances which turn failures into passes are disabled for both engines.
The bridge blocks reference validation and rule execution. Original comparators
are test infrastructure only. The private workload in the motivating screenshot
has not been tested.

Architectural decisions are in [docs/adr](docs/adr). The exact-term dataset avoids
premature literal canonicalization. Documented local Rust dependency patches
preserve RDFLib string identity and SHACL SPARQL prebinding.

PRs use conventional titles and squash merges; `main` requires signed commits,
passing `test`, `compatibility`, `regex`, and `Conventional Commit` checks, and
the configured owner review. Repository maintenance follows the public Legra
release policy and the shared `legra-ai/github-actions` pipeline. Release
artifacts and recovery are described in [releasing](docs/releasing.md).

## License

Original project code is dual-licensed under [MIT](LICENSE-MIT) or
[Apache-2.0](LICENSE-APACHE), at your option (`MIT OR Apache-2.0`).
Copyright 2026 DataRoad Inc, Delaware, USA, trading as Legra.
Vendored code and assets retain their licenses and provenance.
