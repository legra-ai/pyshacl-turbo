# ADR 0032: Measure native execution and publish separate coverage badges

Status: Accepted

ADR 0014's 100% Python requirement covers wrappers, not the native engine. Add
stable-compiler LLVM source coverage for owned Rust, collecting Rust test
executables and Python integration tests against a separately built instrumented
wheel. Do not substitute a normal development extension or sum percentages.

Use Rust 1.99.1, its matching llvm-tools-preview component and cargo-llvm-cov 0.9.1.
Keep the coverage target, per-run profile directories and per-run Python venv
separate from normal builds. Verify the loaded extension resides in that venv and
matches the built wheel bytes. Report Rust-only, Python-only and combined counters.
The shared RDFLib runtime additionally measures the OWL-RL companion suite.

Count every owned src/*.rs file or require an explicitly recorded, hash-checked
declaration-only file with no executable LLVM mapping. Compare each report's
line/region/function denominator with LLVM's complete empty-profile mapping of
the same binaries. Missing files, changed mappings, missing profiles and absent
Python-to-native execution fail the job.

The owned-source denominator excludes separate test-source files, build scripts
and external/vendored dependencies. Inline Rust test modules remain in LLVM's
mapping. Report that scope explicitly. Stable instrumentation measures lines,
regions and functions; Rust branch coverage remains unmeasured. Preserve raw
exports and profiles rather than presenting Python coverage as Rust coverage.

Make native measurement a required dependency of the aggregate release test job.
Publish separate Python-line, Python-branch, Rust-line, Rust-region and
Rust-function badges and HTML reports to GitHub Pages only after successful
main-branch checks. Check that report revisions match the tested source; never
replace missing data with previous numbers. Keep the last successful public
snapshot when CI fails. PRs retain artifacts but cannot publish Pages.

OWL-RL's native badges describe the shared runtime, not an independently written
reasoner or an isolated percentage of OWL-RL rules. Its CI measures the current
facade tests against an explicitly pinned runtime source revision.
