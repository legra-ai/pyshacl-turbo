# Releases

`ci.yml` is the only PyPI publisher. Merging to `main` or manually dispatching
that workflow selects a version through the shared Legra release actions.
Ordinary documentation and CI changes do not bump an already released version.
Scoped Conventional Commit headers are required, including initial history.

The prepared revision must pass Python/Rust checks, complete Python line and
branch coverage, the corrected non-JS compatibility inventory, regex/evaluator
regressions, package-content checks, and installation tests of every wheel.
All release wheels are built from the tested source distribution. Rust and
Python versions are synchronized through `cargo version-info`; do not edit
versions in an independent publishing script.

The initial artifact matrix is CPython 3.11+ ABI3:

| Platform | Architecture | Minimum platform |
| --- | --- | --- |
| Linux | x86-64, ARM64 | glibc 2.28 |
| macOS | Intel | 10.12 |
| macOS | Apple Silicon | 11.0 |
| Windows | x86-64 | As supported by CPython 3.11+ |

Source builds require Rust 1.98.0 and a platform linker. The source distribution
contains the patched Rust dependency sources and tests. SHACL-JS and known
compatibility limits remain as described in [compatibility](compatibility.md).

## Trusted publisher

The PyPI publisher is bound to GitHub owner `legra-ai`, repository
`pyshacl-turbo`, workflow `ci.yml`, environment `pypi`. GitHub restricts that
environment to `main`. The initial pending publisher creates the project on
first upload. A personal PyPI account can own the project; an organization is
not required and does not change its package name.

## Interrupted publication

Dispatch `ci.yml` on `main`. The preparation action resumes the latest unfinished
release at its original tag before advancing the version. Gates run again at
that revision. Publication restores `release-packages.zip` from the draft
GitHub release, checks its version, revision and per-file SHA-256 hashes, and
compares existing PyPI files with those original archives.

Only missing files are uploaded. A conflicting file, tag, revision or unexpected
registry artifact is a hard error. Do not delete a release bundle or overwrite
its contents with a rebuild; compiler output can differ even for the same
source. Do not bypass gates with a local upload. After verifying every file on
PyPI, the workflow makes the GitHub release public.

PyPI's read API can briefly retain a missing or partial release after accepting
uploads. Final verification makes at most 31 queries, ten seconds apart, while
expected archives remain absent. Hash conflicts, unexpected archives and HTTP
errors other than an absent release fail immediately. Exhausting the visibility
budget also fails and leaves the GitHub release in draft.

`CHANGELOG.md` is generated from history during release, ignored by Git, and
excluded from distributions. Root and nested package license texts are checked
in the actual archives. Rust implementation crates are not published separately.

## Initial publication evidence — 2026-10-11

- [Release preparation PR #15](https://github.com/legra-ai/pyshacl-turbo/pull/15)
  introduced the pipeline and shared actions pinned to
  `42049e5750b05a59356fc6756424ca32c2834eb6`.
- [Version 0.1.0](https://pypi.org/project/pyshacl-turbo/0.1.0/) was published
  from verified, signed revision `2155efa8b2dd0b0c32c3a188f033d483b3250dd6`.
  The immutable `v0.1.0` tag and
  [GitHub release](https://github.com/legra-ai/pyshacl-turbo/releases/tag/v0.1.0)
  identify that revision. Its release bundle records the SHA-256 of the source
  archive and all five platform wheels; all six match PyPI's file hashes.
- [Release run 38155681474](https://github.com/legra-ai/pyshacl-turbo/actions/runs/38155681474)
  passed all platform builds, installation checks, Python/Rust checks,
  compatibility, regex and 100% Python line/branch coverage before upload.
  Its first publication attempt received successful upload responses but then
  encountered a stale 404 from the release JSON API. Attempt 2 restored the
  original bundle, verified all existing hashes, skipped uploads and made the
  GitHub release public. The visibility-wait regression reproduces that failure.
- A clean Python 3.13 environment installed `pyshacl-turbo==0.1.0` from PyPI on
  macOS ARM64 and passed the public API and CLI smoke checks without pySHACL or
  owlrl. Installing the `oxigraph` extra also passed valid/invalid Store checks
  through `validate` and `compile_shapes`.
- Before publication, the owner approved correcting the initial unscoped
  commit header. All 12 commit trees were preserved and replacement commits
  were signed. Original history is retained on
  [`archive/pre-pypi-history-20261011`](https://github.com/legra-ai/pyshacl-turbo/tree/archive/pre-pypi-history-20261011).
  No published tag or release history was rewritten.
- Active rulesets require signatures and `prepare`, `test`, `compatibility`,
  `regex` and `Conventional Commit` checks. Outside contributions require owner
  review; the owner and release-writer App have the documented merge bypass.
  Classic branch protection is absent. Daily Cargo, Python and Actions updates,
  grouped updates, security updates and auto-merge are enabled. The `pypi`
  environment permits only `main`, and the matching trusted publisher performed
  the initial upload without a stored PyPI token.

Remaining policy evidence: this repository has not yet demonstrated a real
Dependabot merge followed by a version bump, or dedicated monitoring for stale
releases and disabled schedules. Recovery after complete upload is proven;
partial-upload recovery has regression coverage but has not been induced on the
live registry. These are limits on adoption evidence, not claims of complete
fleet-policy certification.
