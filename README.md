# pyshacl-turbo

[![PyPI version](https://img.shields.io/pypi/v/pyshacl-turbo)](https://pypi.org/project/pyshacl-turbo/)
[![PyPI downloads](https://img.shields.io/pypi/dm/pyshacl-turbo)](https://pypi.org/project/pyshacl-turbo/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://github.com/legra-ai/pyshacl-turbo/blob/main/pyproject.toml)
[![Rust](https://img.shields.io/badge/Rust-1.99.1%2B-DEA584?logo=rust&logoColor=black)](https://github.com/legra-ai/pyshacl-turbo/blob/main/rust-toolchain.toml)
[![License: MIT OR Apache-2.0](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-blue)](https://github.com/legra-ai/pyshacl-turbo/blob/main/LICENSE-MIT)
[![pySHACL non-JS suite: 100% (403/403)](https://img.shields.io/badge/pySHACL%20non--JS%20suite-100%25-brightgreen)](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/compatibility.md#measurements)

[![Tests and wheels](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/ci.yml)
[![Compatibility](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/compatibility.yml/badge.svg?branch=main)](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/compatibility.yml)
[![Regex](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/regex.yml/badge.svg?branch=main)](https://github.com/legra-ai/pyshacl-turbo/actions/workflows/regex.yml)

[![Python line coverage](https://legra-ai.github.io/pyshacl-turbo/python-lines.svg)](https://legra-ai.github.io/pyshacl-turbo/)
[![Python branch coverage](https://legra-ai.github.io/pyshacl-turbo/python-branches.svg)](https://legra-ai.github.io/pyshacl-turbo/)
[![Rust line coverage](https://legra-ai.github.io/pyshacl-turbo/rust-lines.svg)](https://legra-ai.github.io/pyshacl-turbo/)
[![Rust region coverage](https://legra-ai.github.io/pyshacl-turbo/rust-regions.svg)](https://legra-ai.github.io/pyshacl-turbo/)
[![Rust function coverage](https://legra-ai.github.io/pyshacl-turbo/rust-functions.svg)](https://legra-ai.github.io/pyshacl-turbo/)

SHACL validation for Python, powered by Rust. The goal is a **complete drop-in
replacement for pySHACL**, with additional features and better performance.

Companion turbo projects are
[rdflib-turbo](https://github.com/legra-ai/rdflib-turbo), for native RDF datasets,
parsing and SPARQL, and [owlrl-turbo](https://github.com/legra-ai/owlrl-turbo), for
native RDFS/OWL-RL inference using that dataset runtime. Both begin with limited
alpha APIs. They currently connect to pyshacl-turbo through explicit RDFLib
conversion on the initial releases. The shared-dataset releases accept an
rdflib-turbo Dataset directly: parse with rdflib-turbo, infer with owlrl-turbo's
`inplace=True`, then call `validate(data, shacl_graph=...)` on that same object.
Ordinary validation borrows the native dataset; only the report becomes an RDFLib
graph. The runtime protocol and canonical engine-source fingerprint must match.
See [versioned pipeline benchmarks](https://github.com/legra-ai/pyshacl-turbo/blob/main/benchmarks/releases.md).
The [inference memory report](https://github.com/legra-ai/pyshacl-turbo/blob/ff8e693488115e4a1920308b35e5927084b9a9d2/benchmarks/inference-memory.md) includes measured
before/after heap, process memory and runtime for the shared pipeline.

In our [benchmarks](https://github.com/legra-ai/pyshacl-turbo/blob/main/benchmarks/drop-in.md), Turbo was **27–31× faster for SHACL
rules** and **123–126× faster for SPARQL pattern workloads** than pySHACL 0.40.1
with RDFLib inputs. These measurements include shape compilation, input
conversion and report construction, and require equivalent RDF validation
reports. **Some sparse workloads remain slower.** Results depend on the data,
shapes and input backend; the report includes all workloads, raw samples and
measurement conditions.

Shape compilation, Core validation, SPARQL constraints, targets, rules and
inference execute in Rust. Compile shapes once and reuse them across datasets;
pass RDFLib graphs or PyOxigraph Stores directly. There is no runtime dependency
on pySHACL or owlrl. Native execution releases the Python GIL.

## Compatibility

The adapted pySHACL 0.40.1 non-JS regression suite passes **403/403 cases (100%)**.
The W3C suite passes **120/120 with RDF document inputs** and **119/120 with
RDFLib Graph inputs**. See the [compatibility report](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/compatibility.md#measurements)
for test methodology, suite adaptations and individual results. Passing these
suites does not establish complete drop-in compatibility.

Current releases use the `pyshacl_turbo` import and `pyshacl-turbo` command.
Remote SPARQL endpoint inputs and the HTTP server are not implemented, and some
public APIs, complete inference output and report text still differ from
pySHACL. **SHACL-JS is planned.** Review the
[known limits](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/compatibility.md#known-limits) and
[direct API and CLI comparison](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/direct-contract.md) before migrating.

## Install

Requires Python 3.11+. Wheels are available for Linux x86-64/ARM64 (glibc
2.28+), macOS Intel/Apple Silicon, and Windows x86-64. Rust is only needed when
building from source. The compatibility measurements and remaining limits above
apply to the current release.

Add the package to your [uv project](https://docs.astral.sh/uv/guides/projects/):

```sh
uv add pyshacl-turbo
```

For optional PyOxigraph Store input, use:

```sh
uv add 'pyshacl-turbo[oxigraph]'
```

## Command line

Run validation or rules in your uv project:

```sh
uv run pyshacl-turbo data.ttl -s shapes.ttl
uv run pyshacl-turbo-rules data.ttl -s rules.ttl
```

Or run directly in an isolated [uv tool environment](https://docs.astral.sh/uv/guides/tools/):

```sh
uv tool run pyshacl-turbo data.ttl -s shapes.ttl
uv tool run --from pyshacl-turbo pyshacl-turbo-rules data.ttl -s rules.ttl
```

To install both commands for regular use:

```sh
uv tool install pyshacl-turbo
pyshacl-turbo data.ttl -s shapes.ttl
```

If uv reports that its tool directory is missing from `PATH`, run
`uv tool update-shell` and restart your shell. Tool environments are isolated;
use `uv add` for Python imports in your uv project.
Validation exits with status 0 for conforming data and 1 for violations.

## Build

Requires Rust/Cargo, Python 3.11+ and uv. Development uses Python 3.13.
The repository pins Rust 1.98.0 for compilation and formatting.

```sh
make dev
make check
```

## Python

Shape inspection is available through `pyshacl_turbo.shapes_graph.ShapesGraph`
and `pyshacl_turbo.shape.Shape`. `ShapesGraph(graph).shapes` exposes shape
identities and metadata. Call `shape.set_advanced(True)` before
`shape.focus_nodes(data_graph)` to include SHACL-AF targets. Target discovery
uses the native engine. For repeated calls, prepare the data once and reuse both
the shapes graph and snapshot:

```python
from pyshacl_turbo import ShapesGraph, prepare_target_data

shapes = ShapesGraph(shapes_graph)
targets = prepare_target_data(data_graph)
for shape in shapes.shapes:
    shape.set_advanced(True)
    focus_nodes = shape.focus_nodes(targets)
```

The snapshot parses data once and caches target sets per compiled shape and
advanced-mode setting. Prepare a new snapshot after changing the source data.
See the [snapshot guide](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/targeting.md) for a complete example, mutation
semantics and measured first-use versus repeated-use costs.
Ordinary `shape.focus_nodes(data_graph)` calls always read fresh data and still
pay copying costs. These classes expose inspection and
targeting; their complete reference validation/plugin interfaces remain
compatibility work.

To find shapes targeting one node, use the public reverse lookup:

```python
from rdflib import URIRef
from pyshacl_turbo import compile_shapes

program = compile_shapes(shapes_graph, advanced=True)
matching_shapes = program.targeting(targets, URIRef("urn:example:alice"), skip=())
```

It returns active node-shape identifiers and excludes property shapes. Reusing
prepared data shares a native reverse index across node lookups. See the
[targeting guide](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/targeting.md#which-shapes-target-a-node)
for supported targets and exclusion semantics. Built packages include `py.typed`
so type checkers can discover inline type information.

```python
from pyshacl_turbo import compile_shapes, validate

conforms, report_graph, report_text = validate(
    "data.ttl", shacl_graph="shapes.ttl", advanced=True
)

# Compile once and reuse across independent datasets.
program = compile_shapes("shapes.ttl", advanced=True)
conforms, report_graph, report_text = program.validate("data.ttl")
```

Repeated calls automatically reuse native compilation for matching shapes content,
namespace bindings and compilation options. SPARQL execution also reuses optimized
algebra for matching statements and initially bound variable names. Both caches
retain at most 128 entries; each execution reads current data and bindings.
Explicit `compile_shapes()` still avoids loading and serializing unchanged shapes
on every call. See [automatic preparation](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/preparation.md).

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
See [Store input details](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/store-inputs.md).
Named graphs and blank-node labels are preserved. Literal spellings already
normalized by a caller's Store cannot be recovered. Store rule and inference additions commit
atomically only with `inplace=True`, after successful execution. Only new quads
are committed; concurrent deletion of input quads is not undone.

RDFS and OWL-RL inference are implemented natively and selected with
`inference="rdfs"`, `"owlrl"` or `"both"`. Inferred graphs contain standard RDF:
literal values remain objects, and triples with literal subjects are intentionally
excluded. This is a documented
[inference contract](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/adr/0021-standard-rdf-inference-output.md);
differences involving valid RDF remain subject to compatibility testing.
`owlrl` is installed only by the reference-test extra, not as a runtime backend.

Core and SPARQL patterns support Python-compatible regexes, including
lookarounds and backreferences. Count and length bounds retain exact
arbitrary-precision values. See the compatibility details for
[regexes](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/adr/0015-native-sparql-patterns.md) and
[integer parameters](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/adr/0016-exact-integer-parameters.md).

## Rust

The standalone `pyshacl-turbo-engine` crate accepts exact-term oxrdf Dataset
values and `oxigraph::Store` inputs. `CompiledShapes::validate_store` and
`expand_store` copy a consistent quad snapshot without RDF text conversion.
Their `inplace` flag controls atomic addition of derived quads to the Store.
Compiled programs are shareable across threads; parallelism is caller-controlled.

### Borrowed SPARQL graph architecture

![An in-memory Dataset or open Oxigraph transaction supplies GraphRead; optional union and shapes-overlay views feed QueryGraph and the SPARQL evaluator.](crates/engine/src/architecture.svg)

`GraphRead` streams indexed quads and named-graph metadata from a borrowed Dataset
or an open native transaction. `UnionGraph` exposes the data union in the default
graph and preserves named contexts. `OverlayGraph` then adds a separate borrowed
shapes graph; shapes stay outside the data union. Both views are optional.

`QueryGraph` adapts that logical dataset to the existing SPARQL evaluator's
`QueryableDataset` interface. Parsing, plans, joins, filters and property paths
remain in the evaluator. The adapter preserves empty named graphs, translates
SPARQL's named-graph-only wildcard matching and propagates storage errors.
Transaction reads see pending writes and deletions; the caller owns commit and
rollback. No whole-base snapshot or graph-name collection is introduced by the
adapter. Query execution and result construction retain their own memory costs.

These are Rust foundation APIs: complete transaction-backed SHACL validation and
snapshot-free function callbacks still need adoption. The existing Store
validation APIs described above continue to copy a consistent snapshot.
See the [published Rust API documentation and runnable example](https://legra-ai.github.io/pyshacl-turbo/rustdoc/pyshacl_turbo_engine/#borrowed-sparql-graph-architecture).
Rustdoc is built from the tested revision and published with the main-branch
reports; the diagram is embedded directly and requires no JavaScript renderer.

Shape compilation uses [shacl-structural-model](https://github.com/legra-ai/shacl-structural-model)
with Turbo's exact RDF terms, then prepares native queries, regexes and indexes
for execution. The original graph remains available for reports and source
identity. See [ADR 0017](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/adr/0017-shared-structural-compiler.md).

## Performance

The [companion-project benchmark suite](https://github.com/legra-ai/pyshacl-turbo/blob/main/benchmarks/companions.md) measures
rdflib-turbo, owlrl-turbo and pyshacl-turbo together against their reference
packages, including parsing, queries, inference, RDFLib conversion costs and
complete validation pipelines. Run `make benchmark-companions` for the pinned
published-wheel baseline with raw timing samples and separate peak RSS workers.

The [benchmark results](https://github.com/legra-ai/pyshacl-turbo/blob/main/benchmarks/drop-in.md) compare Core validation,
increasing shape counts, SHACL rules and SPARQL patterns through both RDFLib
and Store inputs. Timings are medians of five interleaved samples on macOS
Apple Silicon with Python 3.13. They include input conversion and report
construction; full RDF report parity is required before timing. File I/O,
process startup and fixture construction are excluded. Background build
activity was observed and is documented in the report.

Fresh RDFLib inputs include shape compilation. Separate measurements show
the effect of reusing compiled shapes and using an already loaded Store.
Sparse targeting can be slower because Turbo copies the input graph even
when few nodes need validation. Small API-call timings with stricter output
and interface checks are in the [direct comparison](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/direct-contract.md).

```sh
make benchmark
```

For repeated focus-node inspection, `make benchmark-targeting` compares ordinary
graph calls with fresh and reused `TargetData` snapshots. The local
[targeting samples](https://github.com/legra-ai/pyshacl-turbo/blob/main/benchmarks/targeting.json) cover ten shapes over 1,000 nodes:

| Target kind | pySHACL | Turbo, ordinary graph | Turbo, fresh snapshot including preparation | Turbo, reused snapshot |
| --- | ---: | ---: | ---: | ---: |
| Core class | 4.487 ms | 196.451 ms | 164.510 ms | 0.059 ms |
| SPARQL | 74.319 ms | 201.575 ms | 167.767 ms | 0.052 ms |

These are medians of five samples after warmup, with every target set checked.
Reused snapshots return cached target sets; the fresh-snapshot column includes
initial evaluation. Reuse helps repeated reads of unchanged data, while ordinary
graph calls and initial preparation still have conversion costs. The samples
record source and native-module hashes for the local working-tree release build.

Earlier measurements cover [inference](https://github.com/legra-ai/pyshacl-turbo/blob/main/benchmarks/current.md),
[compiler integration](https://github.com/legra-ai/pyshacl-turbo/blob/main/benchmarks/structural-model.md),
[Core patterns](https://github.com/legra-ai/pyshacl-turbo/blob/main/benchmarks/pattern-core.md) and
[SPARQL patterns](https://github.com/legra-ai/pyshacl-turbo/blob/main/benchmarks/sparql-patterns.md). Each report records the source
revision or hashes and measurement conditions. Inference timings remain
provisional wherever complete inferred graphs differ, even when validation
reports agree. Reference backend errors are recorded without assigning a
speedup. Benchmark your own workloads before drawing capacity estimates.

```sh
# Run alone, separately from builds and other tests.
uv run --locked --extra test python benchmarks/check_core.py

# Full-report-gated SPARQL regex and replacement comparison.
uv run --locked --extra test python benchmarks/matrix.py --kinds sparql-patterns --repeats 7 --output benchmarks/sparql-patterns.json

# Original SPARQL pipeline comparison, including both reference backends.
make benchmark-pipeline
```

## Verification and architecture

Development uses native uv project commands and the committed `uv.lock`.
Run `make dev` to sync the project and test tools, then `make check`. Add or update
Python dependencies with `uv add`; run Ruff, mypy and pytest through `uv run`.
Build wheels and source distributions with `uv build`. The coverage and release
harnesses create isolated uv projects and install the exact built wheels.

Local regressions compare full reports, rule output, graph mutation, blank-node
identity, namespace handling, Store inputs and errors. Pinned W3C and pySHACL
assets live under tests/w3c and vendor/pyshacl respectively.

```sh
make coverage
make test-compatibility
make test-regex
make test-sparql-evaluator
make test-coverage
uv run --locked --extra test python scripts/run_upstream.py
uv run --locked --extra test python scripts/run_upstream.py --reference
uv run --locked --extra test python scripts/audit_reference_fixture.py
```

The three workflow badges report required CI checks on `main`. Each workflow also runs on
pull requests, daily, and on manual dispatch:

| Workflow | What it verifies |
| --- | --- |
| Tests and wheels | Python and Rust regressions, formatting and lint on Linux Python 3.11/3.13 and macOS Python 3.13; SPARQL evaluator tests with compatibility features disabled and enabled; source archive rebuilt into all five platform wheels. Every wheel is checked with locked `uv add`/`uv sync`/`uv run` projects, the optional Store extra, `uv tool run` and `uv tool install`, including both CLIs and validation exit codes. The release also requires Compatibility and Regex at the same prepared revision. |
| Compatibility | Pinned W3C Core/SPARQL cases through document and Graph APIs, the adapted non-JS pySHACL suite, and direct API/CLI comparisons. Suite adaptations are independently checked against both engines. Detailed reports are uploaded as artifacts. |
| Regex | The patched matcher's full upstream suite, unit tests with Turbo's base features, Python-mode VM regressions, and formatting, using its own pinned test dependencies. |

The [coverage reports](https://legra-ai.github.io/pyshacl-turbo/) update after
successful main-branch CI, including the daily scheduled run. Python lines and
branches are measured separately across the complete `pyshacl_turbo` package;
CI requires **100% line and branch coverage**. Rust lines, regions and functions
measure owned native source exercised by Rust and Python integration tests.
Rust branches and dependency/vendored-patch coverage are not measured.
Each published snapshot records its tested revision and measurement date.

Run `make test-coverage` for Python reports in `htmlcov/`, or
`make test-rust-coverage` for combined native reports in `native-coverage/`.
See [native coverage](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/native-coverage.md)
for measurement scope and provenance. Code coverage is separate from SHACL
compatibility.

A green Compatibility badge means the documented suite baselines hold. The
[compatibility report](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/compatibility.md) records suite adaptations and the
expected W3C Graph difference. CI also runs direct API and CLI comparisons:
previously matching cases and fields must remain equal, while known differences
and reference failures stay visible. These badges do not claim complete pySHACL
compatibility.

Architectural decisions are in [docs/adr](https://github.com/legra-ai/pyshacl-turbo/tree/main/docs/adr). The exact-term dataset avoids
premature literal canonicalization. Documented local Rust dependency patches
preserve RDFLib string identity and SHACL SPARQL prebinding.

PRs use conventional titles and squash merges; `main` requires signed commits,
passing `prepare`, `test`, `compatibility`, `regex`, and `Conventional Commit`
checks, and the configured owner review. Repository maintenance follows the public Legra
release policy and the shared `legra-ai/github-actions` pipeline. Release
artifacts and recovery are described in [releasing](https://github.com/legra-ai/pyshacl-turbo/blob/main/docs/releasing.md).

## License

Original project code is dual-licensed under [MIT](https://github.com/legra-ai/pyshacl-turbo/blob/main/LICENSE-MIT) or
[Apache-2.0](https://github.com/legra-ai/pyshacl-turbo/blob/main/LICENSE-APACHE), at your option (`MIT OR Apache-2.0`).
Copyright 2026 DataRoad Inc, Delaware, USA, trading as Legra.
Vendored code and assets retain their licenses and provenance.
