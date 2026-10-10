# pyshacl-turbo

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
.venv/bin/python scripts/run_upstream.py
.venv/bin/python scripts/run_upstream.py --reference
.venv/bin/python scripts/audit_reference_fixture.py
# CI gate: retain the one known failure and independently audit its reports.
.venv/bin/python scripts/check_upstream.py --output /tmp/upstream-results.json
```

Upstream allowances which turn failures into passes are disabled for both engines.
The bridge blocks reference validation and rule execution. Original comparators
are test infrastructure only. The private workload in the motivating screenshot
has not been tested.

Architectural decisions are in [docs/adr](docs/adr). The exact-term dataset avoids
premature literal canonicalization. Documented local Rust dependency patches
preserve RDFLib string identity and SHACL SPARQL prebinding. Original project code
is dual-licensed under [Apache-2.0](LICENSE-APACHE) or [MIT](LICENSE-MIT), at your
option. Vendored code and assets retain their licenses and provenance.

GitHub CI builds and checks Linux Python 3.11/3.13 and macOS Python 3.13,
including isolated wheel installs without pySHACL or owlrl. PRs use conventional
titles and squash merges; `main` requires signed commits, passing checks and
the configured owner review. Repository settings follow the maintained public
`legra-ai/reqwest-embedded-roots` baseline, with check names adapted to this CI.
