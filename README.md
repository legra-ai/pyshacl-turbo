# pyshacl-turbo

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![Rust stable](https://img.shields.io/badge/Rust-stable-DEA584?logo=rust&logoColor=black)](.github/workflows/ci.yml)
[![License: Apache-2.0 OR MIT](https://img.shields.io/badge/license-Apache--2.0%20OR%20MIT-blue)](#verification-and-architecture)
[![Python coverage measured by pytest-cov](https://legra-ai.github.io/pyshacl-turbo/coverage.svg)](https://legra-ai.github.io/pyshacl-turbo/)

[![Tests and wheels](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/ci.yml)
[![Compatibility](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/compatibility.yml/badge.svg?branch=main)](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/compatibility.yml)
[![Regex](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/regex.yml/badge.svg?branch=main)](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/regex.yml)

A Rust SHACL engine with Python bindings. Shape compilation, Core
validation, SPARQL constraints, targets, rules and inference execute in Rust.
There is no runtime dependency on pySHACL or owlrl. Native execution releases
the Python GIL.

Compatibility work targets **pySHACL 0.40.1, excluding SHACL-JS**. It is incomplete.
The complete upstream run passes **402/403 cases (99.8%)**, including
2 explicitly recorded native equivalents for Python implementation tests. The
remaining failure is an audited incorrect assertion in the reference fixture;
both engines produce equivalent reports. It remains recorded as failed.
The pinned W3C run passed **119/120**. These are separate measurements;
see [compatibility](docs/compatibility.md) and the case-level
[upstream report](docs/upstream-coverage.json).

## Build

Requires Rust/Cargo, Python 3.11+ and uv. Development uses Python 3.13.

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

## Performance

```sh
make benchmark
```

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

```sh
# Run alone, separately from builds and other tests.
.venv/bin/python benchmarks/check_core.py

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
make test-coverage
.venv/bin/python scripts/run_upstream.py
.venv/bin/python scripts/run_upstream.py --reference
.venv/bin/python scripts/audit_reference_fixture.py
```

The three workflow badges report required CI checks on `main`. Each workflow also runs on
pull requests, daily, and on manual dispatch:

| Workflow | What it verifies |
| --- | --- |
| Tests and wheels | Python and Rust regressions, formatting and lint on Linux Python 3.11/3.13 and macOS Python 3.13; built wheels installed with only runtime dependencies, without pySHACL or owlrl. |
| Compatibility | All pinned W3C Core/SPARQL cases, the complete non-JS pySHACL inventory, and an independent audit of the known reference-fixture defect. Case-level JSON and W3C JUnit XML are uploaded as artifacts. |
| Regex | The patched matcher's full upstream suite, unit tests with Turbo's base features, Python-mode VM regressions, and formatting, using its own pinned test dependencies. |

The [Python coverage report](https://legra-ai.github.io/pyshacl-turbo/) measures
the complete `pyshacl_turbo` Python package with `pytest-cov`, including uncovered
files and branches. CI requires at least **72% combined line-and-branch coverage**
on Linux Python 3.13. XML, JSON and HTML reports are uploaded for each run; passing
`main` runs publish the HTML report and measured percentage badge to GitHub Pages.
`make test-coverage` generates the same report locally in `htmlcov/`.
This measures Python API/CLI code coverage; it does not measure Rust code coverage
or SHACL compatibility. No package files are omitted from the denominator.

A green Compatibility badge means the documented baseline holds: **402/403**
strict upstream passes and **119/120** W3C passes. The upstream fixture failure
remains failed in the report and must pass its independent audit; the W3C
divergence remains a strict expected failure. New failures and unexpected W3C
passes fail CI. These badges do not claim complete pySHACL compatibility.

Upstream allowances which turn failures into passes are disabled for both engines.
The bridge blocks reference validation and rule execution. Original comparators
are test infrastructure only. The private workload in the motivating screenshot
has not been tested.

Architectural decisions are in [docs/adr](docs/adr). The exact-term dataset avoids
premature literal canonicalization. Documented local Rust dependency patches
preserve RDFLib string identity and SHACL SPARQL prebinding. Original project code
is dual-licensed under [Apache-2.0](LICENSE-APACHE) or [MIT](LICENSE-MIT), at your
option. Vendored code and assets retain their licenses and provenance.

PRs use conventional titles and squash merges; `main` requires signed commits,
passing `test`, `compatibility`, `regex`, and `Conventional Commit` checks, and
the configured owner review. Repository settings follow the maintained public
`legra-ai/reqwest-embedded-roots` baseline, with check names adapted to this CI.
