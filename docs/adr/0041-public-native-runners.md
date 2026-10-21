# ADR 0041: Public runners over the native engine

Status: Accepted

Expose Validator and RuleExpandRunner as independent public types with their
original module names under pyshacl_turbo. Reuse ADR 0040's live RDFLib DataGraph
views. Share constructor and preparation logic in a private base; a rule runner
is not a validator subtype.

Retain options, logger, shapes graph, target graph, inplace state and the
pre-inferenced flag. Prepare ontology/inference once for each runner, cloning
only when the requested operation requires an independent target. Dataset
ontology additions use the inoculation context. Inference and all validation
and rule evaluation execute through the native engine, never the reference
Python implementation. Rule execution returns the prepared DataGraph wrapper.

Expose the SHACLExecutor settings model and public report construction helper.
Validation uses its configured depth; rule runners retain their distinct executor
policy. Direct validator execution propagates ValidationFailure while the
top-level validate entry point retains its failure-result contract. Manual report
construction formats supplied results, including the reference's bounded report
blank-node cloning behavior; it does not evaluate constraints.

Original package-name aliases, optional PyOxigraph DataGraph backends, shared
native Store graph adapters, SHACL-JS and remote SPARQL execution are separate
parity work. Unsupported backends/modes fail explicitly rather than switching
to another interpreter or copying a foreign native dataset.
