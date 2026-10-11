# ADR 0014: Require complete Python coverage and measure both W3C input paths

Status: Accepted

## Evidence

Expanding the Python line and branch coverage from 72.1% exposed three defects:

- Validation reports requested as N-Quads reached RDFLib's context-aware-only
  serializer as plain Graphs and failed instead of producing a report.
- Combining data inputs discarded namespace bindings. CLI focus names such as
  `ex:s` then selected the wrong IRI and could yield a false conforming result.
- The DASH report comparator checked only the expected report's `sh:conforms`,
  accepting a malformed actual report without that required declaration.

Each defect was reproduced by a failing regression before its fix. Additional
tests execute the actual native engine through the public API, CLI, document
loader, imports, local HTTP retrieval, Graph/Store mutation, and DASH adapters.
RDFLib's N-Triples serializer emits exactly one triple per line and no lines for
an empty graph. After testing empty contexts and escaped literal newlines, remove
the unreachable blank-line filter from that serializer's consumer.

## Decision

Require 100% coverage of both lines and branches in the complete Python package.
Keep every package file in the measured source, including entrypoints. Do not
add coverage exclusions or omit error branches. Native Rust coverage remains a
separate, unmeasured quantity; the Python percentage must not stand in for it.

Serialize context-aware CLI formats through a Dataset while preserving namespace
bindings. Retain source namespace bindings when combining input graphs. Reject
an actual DASH report without `sh:conforms` with a hard error.

Preserve ADR 0007's input-dependent boolean behavior. Add a complete W3C document
run alongside the existing Graph run, using the same unmodified 120 fixtures.
Both runs are required CI checks. Independent parses assign different blank-node
labels: compare their descriptions and shared references in document reports,
while retaining exact input-node identity for Graph reports. Keep all report
fields, multiplicities and structural path checks under the existing W3C rules.
Comparator regressions reject changed fields, missing/duplicate results, changed
anonymous shape definitions, and changed blank-node sharing.

## Measurements

Document inputs pass 120/120 W3C cases. Graph inputs still pass 119/120, retaining
the strict expected failure for `uniqueLang-002`. Record both denominators and
results separately. The new run measures another public API path; it is not an
engine fix for the original Graph discrepancy.

The strict non-JS upstream suite remains 402/403. Its last assertion contradicts
both engines' isomorphic nonconforming reports. Keep that failure and the
immutable-fixture audit; changing its status to manufacture 100% would violate
ADRs 0005 and 0009. Complete code coverage and a passing finite fixture set do
not establish universal pySHACL compatibility.
