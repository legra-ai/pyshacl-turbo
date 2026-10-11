# ADR 0015: Native Python regex behavior in SPARQL and exact callback terms

Status: Accepted

## Evidence

ADR 0013 aligned Core `sh:pattern` with Python, but SPARQL REGEX and REPLACE
still used Oxigraph's matcher. Differential regressions reproduced failures
with lookarounds, backreferences, Unicode classes, flags and replacement text.
The initial 57-case addition had 46 failures before implementation changes.

Further regressions found two independent losses of RDF term identity:
spareval converted custom-function inputs and outputs through expression values,
canonicalizing `"01"^^xsd:integer` and collapsing explicit `xsd:string`; the
SPARQL JSON writer also omitted an explicit string datatype. A target regression
exposed different default min/max-count report messages. Each failure was
reproduced against the pinned reference before its fix.

## Decision

Lower REGEX and REPLACE in parsed SPARQL algebra to private native scalar
functions. Visit nested expressions, subqueries, aggregates, ordering and EXISTS;
do not rewrite query text. Apply the lowering to constraints, targets, rules,
SHACL functions and the native query API. Reuse ADR 0013's Python pattern
translator and patched native matcher. No Python regex or query engine is used.

REGEX recognizes lowercase `i`, `m` and `s`, matching RDFLib 7.6.0. Core flags
retain their separate contract. REPLACE reproduces the pinned RDFLib behavior:
its Python flag mask is passed as `re.sub`'s replacement count, not as flags.
Inline pattern flags still apply. Preserve dollar-to-backslash conversion,
Python numbered/named group references, replacement escapes, unmatched groups,
and Python's empty-match advancement rules. Parse replacement templates even
when the pattern will not match. Respect the reference's false flag values.

Share a bounded 128-entry compiled-pattern cache across uses of an immutable
query. Each evaluation gets a fresh hard-error slot, including concurrent
validations. Compilation, replacement-template and backtracking failures remain
errors through lazy query-result iteration. Ordinary RDF argument type errors
remain SPARQL expression errors. Failed validation never commits derived quads.
Queries without regex or registered SHACL functions retain the prepared fast path.

Enable spareval's new opt-in `exact-custom-function-terms` feature. Pass raw RDF
terms across callback boundaries and internalize their results without value
canonicalization. Enclosing arithmetic or other value expressions still request
expression values normally. Preserve upstream callback behavior when the feature
is disabled; test both modes independently from the workspace's feature set.

Serialize native SELECT/ASK JSON with explicit RDF datatype and language
information, including explicit `xsd:string`. Produce pySHACL's default
min/max-count messages from the compiled count, focus node and result path;
custom shape messages retain precedence.

## Verification and limits

`tests/test_sparql_patterns.py` adds 104 differential and failure regressions,
including full reports, rule output, query results, literal identity, callback
errors, mutation and concurrent reuse. The 82 Core pattern regressions continue
to pass. `make test-sparql-evaluator` runs the vendored evaluator's unit suite
with default behavior and with both Turbo compatibility features; CI requires it.

The strict upstream inventory remains 402/403, with its audited incorrect
reference assertion still failed. These new regressions exercise gaps outside
that inventory and do not change its denominator. Python coverage remains a
separate measurement. Regex parser diagnostics, Unicode database alignment and
Python 3.14 changes retain ADR 0013's limits. A finite suite does not establish
universal pySHACL or Python regex compatibility.

The `sparql-patterns` benchmark includes native REGEX and REPLACE with full
report parity required before timing. Its common-syntax expressions allow a
comparison with both RDFLib and PyOxigraph reference backends; specialized
Python constructs are covered by the differential tests instead.
String inputs use explicit `xsd:string` so the RDFLib and Store adapters receive
equivalent literal terms and preserve identical `sh:value` statements in reports.
