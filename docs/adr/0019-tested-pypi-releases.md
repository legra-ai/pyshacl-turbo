# ADR 0019: Publish tested Python distributions through one release pipeline

Status: Accepted

## Evidence

The owner requested PyPI publication after reviewing Legra's public repository
policy. The maintained `tasktree` and `dotenvage` pipelines use shared release
preparation, an exact tested revision, a draft GitHub release, and resumable
registry publication. The previous Turbo source distribution contained neither
the patched Rust dependency sources nor the Python regression suite. A wheel
built directly from the checkout did not prove the source archive was usable.

## Decision

Use `ci.yml` as the only publisher. The shared preparation action selects the
version and revision. Every gate and artifact job checks out that revision;
compatibility and regex workflows also accept it as a reusable-workflow input.
The aggregate `test` gate requires all of them. Keep the standalone workflows
for their existing branch badges and required checks.

Build one source archive with the patched dependencies, regression fixtures,
license texts and pinned Rust toolchain. Build all five CPython 3.11+ ABI3 wheels
from that archive: Linux x86-64 and ARM64 (glibc 2.28+), macOS Intel and Apple
Silicon, and Windows x86-64. Check package contents and metadata; install each
wheel on its native platform without pySHACL or owlrl and run the public API
and CLI smoke checks. This does not claim full platform-specific compatibility
from those smoke checks alone.

Both Rust workspace members are implementation packages with `publish = false`.
Their source remains in the Python source distribution. Separate crates.io
publication would require a decision about the patched dependencies. Use a
declared cargo-version-info hook to synchronize the Python version. Rhusky
installs repository hooks; its installer and repository opt-in do not ship in
the source distribution.

Only after all gates pass, create the immutable version tag and draft GitHub
release. Persist the original six archives in a release bundle containing the
source revision and SHA-256 hashes. Retries restore that bundle, require matching
registry hashes for existing files, and upload only missing files. Different or
unexpected files fail immediately. Publish the GitHub release only after all
six files are verified on PyPI. Never use `skip-existing` to hide a mismatch.

The initial release exposed delayed visibility in PyPI's release JSON API after
successful uploads. Final verification therefore allows at most 31 reads, ten
seconds apart, for missing archives to appear. Conflicting bytes, unexpected
files and other HTTP errors still fail immediately; an exhausted visibility
budget leaves the GitHub release in draft.

Use PyPI trusted publishing for this repository, `ci.yml`, and the `pypi`
environment restricted to `main`. No long-lived PyPI token is required. A
manually dispatched run follows the same gates and resumes the original tag.

## Consequences

Scoped Conventional Commit validation also applies to initial release history.
An invalid historical header blocks preparation; this pipeline does not hide
it with an exception, bootstrap tag, replacement Git object or manual upload.
Compatibility and coverage claims retain the separate denominators and limits
defined by earlier ADRs. Public registry badges are added after the first
successful publication.
