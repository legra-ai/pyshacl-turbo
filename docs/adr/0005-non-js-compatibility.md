# ADR 0005: Execute the complete pinned non-JS compatibility suite

Status: Accepted

## Context

The user requested continuation until 100% pySHACL compatibility excluding JS.
W3C conformance alone does not measure pySHACL's API and advanced features.

## Decision

Run every non-JS upstream test function, expanding parametrization, at the pinned
0.40.1 revision. Include functions in package initializers and nonstandard test
filenames. Record collection errors, skipped cases and unexecuted cases; none is
a pass. Disable upstream lists which turn failures into successful tests. Keep a
separate reference run to distinguish pre-existing reference failures.

The test-only bridge redirects public API calls and subprocesses to turbo and
blocks the original validator and rule runner. Reference report comparators are
test infrastructure only. Tests coupled to Python implementation internals must
have explicit equivalent Rust regressions; never count the reference code's
execution as turbo compatibility.

Expand the native engine and Python I/O boundary to implement inference, graph
and dataset loading, API options, advanced features and CLI behavior. This
supersedes the corresponding temporary unsupported-feature limits in ADRs 0001
and 0002. Rust still executes all SHACL, SPARQL and inference. Python may parse
and serialize boundary formats, retrieve input documents and adapt API objects.
No runtime reference validator or inference fallback is permitted.

## Measurement

Keep upstream compatibility separate from W3C conformance and the local
regression suite. A percentage always identifies its denominator and exclusions.
The existing W3C uniqueLang disagreement remains explicitly reported.
