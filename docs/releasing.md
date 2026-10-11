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

`CHANGELOG.md` is generated from history during release, ignored by Git, and
excluded from distributions. Root and nested package license texts are checked
in the actual archives. Rust implementation crates are not published separately.
