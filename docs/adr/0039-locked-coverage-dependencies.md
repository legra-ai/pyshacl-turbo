# ADR 0039: Derive coverage dependencies from the authoritative uv lock

Status: Accepted

Supersedes ADR 0034's committed requirements snapshot for native coverage.
The test extra in pyproject.toml and its resolution in uv.lock are authoritative.
A separately committed export can drift after dependency updates, so remove it
and its source-distribution include. Contract fingerprints include uv.lock.

Before initializing the isolated measurement project, run uv export --locked
with the explicit source project, test extra, no development group, no emitted
source project and no hashes. Write the export under the measurement profiles
directory. A stale lock, unsupported source identity or export failure aborts
before dependency installation; never retry with an unlocked or legacy input.
The export must not modify the source metadata or lock.

Import the generated requirements through uv add and uv sync --locked in the
separate test project. Install the exact instrumented wheel there and retain
the existing loaded-extension byte checks, isolated Python invocation and
owned-source coverage denominator. Source imports cannot replace wheel tests.

Preserve source metadata, source uv.lock, the generated export and actual
environment locks with the report. Record source/export hashes, selection and
uv version. Preserve the environment lock separately for Rust, Python and any
companion stage. Verify source and preserved export bytes again before writing
the final report, so measurements cannot claim changed dependency inputs.
