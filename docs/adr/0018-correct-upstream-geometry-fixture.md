# ADR 0018: Correct the upstream geometry fixture expectation

Status: Accepted

## Evidence

The user authorized correcting the final failing upstream test after reviewing
why both engines reject its data. Before this change, the actual
`test/issues/bad_test_070.py::test_070` failed at `assert conforms` with both
pySHACL 0.40.1 and Turbo. Its geometry node has type `sf:Point`, but the input
does not supply a `geo:Geometry` type or a subclass relationship connecting the
two classes. The shapes require `geo:Geometry` on `geo:hasGeometry` values.
Both engines correctly report the same single class violation.

The test's expectation, rather than validator behavior, is defective. Treating
its failure as a permanent CI exception obscures whether the test is meaningful.

## Decision

Apply a documented local patch to the vendored upstream test, for both engines.
Pin its remote shapes URL to the immutable revision already used by the fixture
audit. Assert nonconformance and the exact violation's constraint component,
focus node, path and value. Then add
`sf:Point rdfs:subClassOf geo:Geometry` to the same data graph and require
conformance with no results. No engine implementation changes are needed.

Run the corrected test itself in the independent audit with both engines,
using identical checksum-verified shapes bytes. Compare their complete report
graphs for both the invalid and repaired inputs. Keep the audit's source and
fixture hashes and the explicit correction path in its output.

The suite refresh script reapplies `vendor/pyshacl-issue-70.patch` and records
its checksum. A patch failure is a hard error. Both upstream reports mark the
case with `local_correction`; the original case ID and 403-case denominator
remain unchanged. The two native equivalents remain separately identified.

Remove the CI exception for the old assertion failure. Require exit status
zero, every inventoried case passed, no collection errors or skipped cases,
and unchanged correction/native-equivalent mappings. A regression test ensures
the formerly allowed `assert False` failure is rejected.

## Measurement

Report **403/403 in the locally corrected suite**: 400 unchanged behavioral
cases, one corrected fixture and two native equivalents. This supersedes the
decision to retain the known fixture failure in ADR 0011 and the historical
402/403 measurements in later ADRs. The unmodified upstream test still has the
incorrect assertion; no upstream change is claimed. The reference run improves
from 400/403 to 401/403, retaining its two unrelated `shapesGraph-001` failures.

W3C Graph/document results, Python coverage and known compatibility limits are
separate measurements and remain unchanged. Passing this finite corrected
inventory is not proof of universal pySHACL compatibility.
