# ADR 0003: Preserve RDF terms through storage, queries and Python output

Status: Accepted

## Evidence

The expanded W3C suite and native regression demonstrate that Oxigraph Store
collapses `"01"^^xsd:integer` with `"1"^^xsd:integer`, changes `"4.0"^^xsd:decimal`
to `"4"^^xsd:decimal`, and returns `"300"^^xsd:byte` as an integer. These changes
alter cardinality, datatype validation and report values. Reconstructing original
terms from numeric values cannot fix this because multiple original terms can
have the same value.

## Decision

Use Oxigraph's `oxrdf::Dataset` for exact term storage and bind the existing
prepared SPARQL evaluator through `on_queryable_dataset`. This is the sole native
execution path. Change the Rust API to explicit `&mut Dataset` for operations
that expand rules; remove the old Store contract. Python output decoding must
construct literals with `normalize=False` without changing RDFLib's process-wide
normalization flag. Test both direct constraint execution and CONSTRUCT copying.

## Consequences

This supersedes the Store API in ADR 0001. The Rust caller owns its dataset and
may observe rule additions after an error. Python continues to commit inplace
additions only on success. Python inputs already normalized by their caller
cannot be repaired; native file/text parsing preserves their original terms.

W3C `uniqueLang-002` expects `"1"^^xsd:boolean` not to activate uniqueLang.
pySHACL 0.40.1 activates it, even with RDFLib normalization disabled. Preserve
pySHACL's boolean-value behavior and record this W3C disagreement explicitly.
It is not a passing conformance case.

## Reference report-description copying

The exact-term input, storage, query and rule-output boundary remains unchanged.
A validation report has a separate compatibility operation: pySHACL reconstructs
literal objects while copying a referenced blank node's description into the
report. Its `clone_literal` calls `rdflib.Literal` without a normalization override.
Direct literal focus/value results are reused rather than copied.

The top-level reference `validate` temporarily patches shape loading and then
sets RDFLib normalization to True before report creation, even when the caller
had disabled it. Match that report-copy result with an explicit per-call True
setting, without changing the process-wide flag. Direct Validator/report-builder
and reusable CompiledShapes calls honor the caller's current normalization setting.
Only literal objects under report-referenced blank descriptions are reconstructed;
source graphs, native storage, direct result terms and ordinary RDF decoding keep
their exact terms. Traverse decoded report nodes with a visited set, retaining
cycles, reused references and list/path topology within the report output.

A report-copy warning promoted to an exception must occur before accepting staged
native rules or committing standalone inplace output. Differential regressions
cover both RDFLib normalization settings, nested descriptions, direct result
literals and caller signal policy. This exception is report construction, not a
permission to normalize execution inputs or repair native RDF output generally.
