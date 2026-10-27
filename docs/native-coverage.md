# Native coverage

The façade has one Python package and no Rust implementation. Its exact declared
rdflib-turbo dependency owns the native SHACL engine, bindings, patched dependencies,
and sole native coverage collector. The façade workflows delegate to that owner;
they do not maintain a second source denominator or copy of the collector.

Python lines, Python branches, Rust lines, Rust regions and Rust functions remain
separate badges. Successful main-branch CI publishes reports and badges to
[GitHub Pages](https://legra-ai.github.io/pyshacl-turbo/). Failed CI preserves the
last successful snapshot, including its tested revision and measurement date.
PRs upload measurements and provenance without publishing Pages.

To reproduce the owner measurement, install its pinned compiler and LLVM tools
and cargo-llvm-cov 0.9.1. Build the original façade archive and universal wheel
outside the frozen checkout, then invoke the owner driver:

```sh
uv build --sdist --out-dir ../coverage-inputs/source
uv build --wheel --out-dir ../coverage-inputs/wheel ../coverage-inputs/source/*.tar.gz
uv run --no-project --python 3.13 python -B scripts/owner_driver.py \
  --facade-source "$PWD" \
  --facade-wheel ../coverage-inputs/wheel/pyshacl_turbo-*-py3-none-any.whl \
  --output ../coverage-work --gate coverage
```

Use a clean committed façade checkout and a new output directory. The driver
first verifies that the exact declared published provider exposes the required
native classes and protocol. An incapable registry release fails before native
compilation. It downloads original registry source and wheel archives and verifies
their recorded SHA-256 values, package bytes, local engine ownership, exact
compiler/build profile and independently derived engine fingerprint. The current
façade acceptance source is separate from the provider's UV-locked declaration
peer. Both roles and the original OWL companion source have explicit authority.

Only that verified provider collector builds the instrumented native wheel. It
runs Rust, provider Python, façade Python and OWL integration tests and merges the
five-stage coverage profiles. The instrumented wheel's actual bytes and loaded
module identity are checked before execution. Façade Python coverage requires
100% lines and branches. The driver also runs the owner's formatting, Clippy,
datatype, evaluator, dataset, storage and allocation gates and builds its Rust API
documentation. The existing Regex workflow separately runs the owner's full
matcher profiles and semantic guards. Final checks reattest all source, archive,
project-lock and installed-package payloads.

`python -B` and bytecode-disabled child environments preserve the strict original
source inventories. Generated files are never silently accepted as original source.
The `native-coverage` subdirectory contains the sole collector's summary, complete
source counts, raw exports, merged profiles and HTML. Adjacent receipts identify
original archives, current façade source, native payload, source fingerprint and
gate results; `rustdoc/doc` contains the verified owner's API documentation.

Rust percentages measure the provider's owned source. The provider's audited
source inventory defines any declaration-only file without executable LLVM
mapping. A source change requires a fresh mapping audit; a matching inventory hash
cannot exclude a file that has executable mappings. Missing owned files or
shrinking denominators fail verification. Dependency and vendored-patch coverage,
Rust branch coverage, doctests and standards conformance remain separate measures.
No uncovered region receives synthetic hits, and partial percentages are never
rounded up to 100%.

The historical [native coverage ADR](adr/0032-native-rust-coverage.md) and
[first baseline](native-coverage-baseline.json) record the earlier ownership
layout. New reports identify the actual provider authority rather than treating
those historical source paths as current façade implementation.

## Shared performance inputs

The shared performance workflow prepares original façade archives with uv, then
resolves the exact declared published provider before any native compilation.
The provider's UV lock selects the published OWL source and universal wheel.
Original registry hashes and source inventories remain authoritative; no Git
revision is guessed from a package version.

```sh
uv run --no-project --python 3.13 python -B scripts/build_published_benchmark.py \
  --output ../pipeline-inputs
```

The native candidate is built in RELEASE mode from that original provider sdist.
The builder verifies the source fingerprint, installed package bytes, shared
classes and Store behavior before emitting `candidate/candidate-wheels` and its
source manifest. Direct candidate installation and registry installation have
separate checks. Original artifacts and build/launch receipts are retained.
External Cargo build/target flags and profile overrides are rejected; configured
compiler cache wrappers are preserved and recorded.

Input eligibility does not establish reference equality or a performance result.
The existing `benchmarks/releases.py` worker must complete its output comparisons
before the workflow can publish a version table. An incapable published provider
fails the workflow before native compilation; it is never replaced with an
unreleased source or treated as a passing benchmark.
