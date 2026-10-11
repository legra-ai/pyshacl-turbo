# ADR 0016: Exact integer domains for count and length parameters

Status: Accepted

## Evidence

Reviewing `shacl-structural-model`'s generic count parameter highlighted Turbo's
shared `u64` restriction. Differential tests confirmed that pySHACL accepts
`sh:minCount 18446744073709551616` and larger bounds while Turbo raised an error.
The same restriction affected length and qualified-count constraints.

The initial corrected 79-case regression set produced 61 failures. It exposed
parameter-specific datatype rules, default messages and zero minimum length on
blank nodes. Further tests reproduced qualified-count empty-batch differences,
Unicode digit rejection and overly permissive underscore parsing. A Rust debug
test also reproduced a digit-parser overflow before the implementation was fixed.

## Decision

Keep each integer declaration's original literal and an exact `BigInt` comparison
value. Compare actual collection/string sizes against that value without narrowing,
clamping or floating-point conversion. Retain the original datatype and lexical
form for report messages. No Python parser or reasoner is called.

Match the pinned pySHACL 0.40.1 parameter domains separately:

- `minCount` and `maxCount` require nonnegative `xsd:integer` literals.
- `minLength` and `maxLength` accept the reference's whole-integer datatype list
  and reject negative values. Preserve its explicit exclusion of `xsd:byte`,
  `xsd:negativeInteger` and `xsd:nonPositiveInteger`, including zero values.
- Qualified counts use the reference's integer-value test, which also accepts
  signed integer subtypes and booleans. Boolean declarations retain Python's
  `True`/`False` spelling in default messages.

Parse optional signs, surrounding whitespace, Unicode decimal digits and single
underscores between digits. Reject malformed input before handing normalized
digits to BigInt, whose own underscore parser is more permissive. Matching uses
Rust Unicode decimal-digit tables. Invalid parameters are hard errors.

Reproduce default length and qualified-count messages. A zero minimum length
accepts blank nodes, matching the pinned reference. Qualified counts skip an
empty batch when their minimum allows zero and disjoint mode is disabled. Track
that batch across top-level focus nodes; nested property validation receives a
separate one-node batch. Restore batch state on success and error, with no shared
mutable state across compiled-program calls.

## Verification and limits

`tests/test_integer_parameters.py` adds 141 differential/error cases, comparing
complete RDF reports. Coverage includes bounds above `u64::MAX`, 101-digit
integers, derived datatypes, signed and boolean qualified counts, noncanonical
lexical forms, malformed input, nested focus scopes and empty batches. A native
debug regression requires malformed literals to return errors without panicking.

The entire strict upstream inventory and both W3C input paths remain required.
These additional cases do not change their denominators. Python coverage is
still measured independently. Version-specific Unicode tables and configurable
Python integer-parser limits remain outside this finite compatibility evidence.

The shared structural model could carry these exact values and compiled count
types, but adoption also requires blank-node identifiers, RDF-valued messages
and the SPARQL/AF declarations already supported by Turbo. This decision does
not add that dependency or replace Turbo's compiled execution structures.

Reviewed structural-model revision:
[`316cccb`](https://github.com/legra-ai/shacl-structural-model/tree/316cccb30f7b004b2ff71bd32f7edb012eb15f24).
