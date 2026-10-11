# Vendored sources

- `pyshacl/`: test assets and license from RDFLib/pySHACL commit
  `469cca7a22a078b36c167c1e8dadecf5e5ec6c75` (v0.40.1). This is an inventory for
  compatibility work, not a production dependency. The complete non-JS inventory
  executes 403 parametrized cases, including two explicitly documented native
  equivalents; case-level results are in `../docs/upstream-coverage.json`.
- `sparopt-0.3.7/`, `spareval-0.2.7/`: published Oxigraph crate sources, from
  revision `0e81a29d27575ab69e7f85ea9c7f1058b277fcd0`. Original archive checksums
  are in `rust-sources.json`; MIT and Apache license texts are retained.
  Initial bound-variable handling is patched in `sparql-prebinding.patch`,
  explained in [ADR 0004](../docs/adr/0004-sparql-prebinding.md). The spareval
  opt-in undefined scalar-function feature is documented in its `TURBO-PATCH.md`
  and [ADR 0012](../docs/adr/0012-reference-recursion-and-expression-errors.md).
  Its opt-in exact callback-term feature is documented in the same patch note
  and [ADR 0015](../docs/adr/0015-native-sparql-patterns.md). CI tests default
  behavior and both enabled features using `make test-sparql-evaluator`.
- `spargebra-0.4.7/`: projection parsing accepts explicitly supplied external
  variables for SHACL prebindings; see its `TURBO-PATCH.md`.
- `oxrdf-0.3.4/`: optional exact string term identity, documented in its
  `TURBO-PATCH.md` and [ADR 0011](../docs/adr/0011-literal-identity-and-report-graph-scope.md).
- `fancy-regex-0.19.2/`: published crate with an opt-in Python backreference
  and lookaround feature, documented in its `TURBO-PATCH.md`. Original checksum
  and revision are in `rust-sources.json`; its MIT license is retained.

No upstream PRs have been submitted for these local Rust patches.

`../scripts/sync_suites.py` refreshes the pinned W3C and pySHACL test assets.
It does not overwrite the patched Rust dependencies.
