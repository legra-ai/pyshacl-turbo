# ADR 0017: Compile through the shared SHACL structural model

Status: Accepted

## Evidence

Turbo previously read RDF triples directly into execution structures. The
declaration reader and query/index preparation were coupled, so sharing typed
SHACL values with other tools required a second representation and parser.

`shacl-structural-model` can carry Turbo's exact RDF terms without converting
through text, JSON or another RDF library. Integration regressions exposed two
important boundaries: implicit classes and target types can be blank nodes,
and display-only `sh:defaultValue` annotations do not trigger cardinality
validation in pySHACL. The target identities were fixed in structural-model
3.0.0; the compiler leaves display defaults in the original source graph.

## Decision

Pin the released `shacl-structural-model` crate. Read each discovered shape into
its `NodeShape<Term>` or `PropertyShape<Term>`, then consume that declaration
into Turbo's execution structures. Use the model's Core components, paths,
targets, query declarations, parameters, component applications, functions,
rules and node expressions as compiler inputs. There is no second direct-RDF
compiler. No document-sized structural schema is retained: each shape is
lowered and discarded while the compiled program is assembled.

The value and count types are Turbo's patched Oxigraph `Term`. This preserves
blank nodes, plain versus explicit `xsd:string` literals, language tags, custom
severity IRIs, numeric lexical forms and arbitrary-size count parameters.
Interpret counts with ADR 0016's existing integer compiler. Interpret execution
order as `BigDecimal`, with no float conversion. Prepared queries, translated
regexes, shape indexes and paths remain native execution structures. Validation
does not traverse the shared structural model on every call.

Keep the original RDF dataset for reports, `$shapesGraph`, path/list identity
and annotations. Apply ADR 0007's graph/document boolean policy to the compiler
input before reading declarations, without rewriting the retained source.
The reader is an execution projection, not a complete RDF-to-model export API.
Unused display metadata and parameter constraints remain source annotations.
ADR 0010 still controls executable shape roles.

Resolve references from the shared declarations at compilation time. Prefix
resources and imports become typed declarations when reached. Cross-shape
relationships for closed shapes and disjoint qualified siblings still consult
the source graph. Query text, messages, supplied parameter values and constraint
values come from the model, rather than being read a second time during lowering.

Custom component discovery retains validator resource references. Only an
active component application resolves its applicable node, property or generic
validator into a model declaration. This preserves unused metadata behavior
and validator-role precedence. Malformed active queries still fail immediately.
Keep existing SPARQL-over-TripleRule precedence, function parameter ordering
and pySHACL's focus-based path-expression semantics.

This changes the internal compiler boundary, not the Python input API or the
supported SHACL language. pySHACL and owlrl remain reference-test dependencies
only. The structural crate does not supply an execution engine or reasoner.

## Verification and limits

Native regression tests cover model-to-compiler consumption, exact RDF terms,
blank-node shape/target identities, multilingual messages, arbitrary counts,
decimal rule order, source path nodes, conditions, custom binding combinations,
inactive validator roles, original graph retention and compiled-program reuse.
Python differential tests cover named/blank custom target types and ignored
display defaults against pySHACL 0.40.1.

The complete test and benchmark results are recorded in the integration PR and
the [compiler comparison](../../benchmarks/structural-model.md). Compatibility
percentages retain their existing denominators. In particular, the one audited
incorrect upstream assertion remains failed; a compiler refactor cannot turn
that inventory into proof of universal pySHACL compatibility.
