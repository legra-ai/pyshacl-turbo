# Native coverage

The README badges are generated from CI observations, not hard-coded percentages.
Python lines, Python branches, Rust lines, Rust regions and Rust functions are
separate badges. Successful main-branch CI, including the daily scheduled run,
publishes the reports and badges to [GitHub Pages](https://legra-ai.github.io/pyshacl-turbo/).
PRs upload report artifacts without publishing. Failed CI leaves the last
successful snapshot intact; the public report records its tested revision/date.

Install the pinned tools, then run from a checkout:

```sh
rustup component add llvm-tools-preview --toolchain 1.99.1
cargo install cargo-llvm-cov --version 0.9.1 --locked
make test-rust-coverage
```

The harness uses the current repository source and pinned test dependencies in a
fresh venv. It builds an instrumented wheel without changing a normal development
extension, verifies the loaded bytes, runs Rust tests and the Python suite, and
merges the runtime profiles. Python integration also emits Python line/branch JSON
and HTML with the existing 100% requirement. Results appear in `native-coverage/`:
summary JSON/Markdown, per-file counts, detailed LLVM JSON exports, merged
profiles and HTML. [The first baseline](native-coverage-baseline.json) records
source hashes, compiler/tool versions and the original observations.

See [ADR 0032](adr/0032-native-rust-coverage.md) for the denominator. One source
file contains declarations and a derived enum with no executable LLVM mapping.
Its exact content is audited by `native-coverage-sources.json`; changing it
requires reviewing the zero-mapping classification. It is not treated as covered.
Other owned source files must appear in every report.

The initial LLVM build also reports an unexecuted generated `PyInit__native`
hash variant from PyO3's external module bootstrap when test and extension
objects are read together. Raw diagnostics remain in CI logs. Every owned
file's complete line/region/function denominator is checked independently against
LLVM's empty-profile mapping, so a missing owned mapping cannot silently shrink
the result.

Percentages cover owned Rust source. Dependency and vendored-patch coverage,
stable-Rust branch coverage, doctests and standards conformance are separate,
unmeasured quantities. Inline test modules remain in LLVM's source mapping.
There is no numerical Rust threshold for this initial measurement; inventory,
instrumented-wheel identity, native execution and report consistency are mandatory
CI gates. Badge percentages round down to a tenth, never up to 100%.


Standalone native tests now cover internal graph helpers, malformed declarations,
inference atomicity and boundary failures alongside public Python integration.
Remaining unexecuted regions stay in the denominator. Examples include errors
from serializing valid RDF into an in-memory byte vector, parsing built-in query
constants and impossible result variants after query-kind validation. These are
not assigned synthetic hits. The HTML report is the per-revision gap inventory;
a high aggregate percentage does not establish exhaustive behavioral coverage.

The Rust test executables embed the selected Python distribution. Their runtime
uses that interpreter's absolute base prefix, separately from the wheel-test
venv, so relocatable Python installations load the matching standard library.
The shared datatype parser correction and required upstream tests are recorded
in the datatype-parser ADR and vendored patch note.
