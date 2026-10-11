# ADR 0020: Measure the complete public replacement contract

Status: Accepted

## Context

The target is a complete drop-in replacement for pySHACL, with additional
features and better performance. The owner has explicitly included SHACL-JS
as future work. This supersedes the permanent JS exclusion in ADR 0005; the
existing 403-case suite remains a non-JS measurement with the same denominator.

A direct audit found gaps outside that passing suite: `validate_each` returned
a list instead of an indexed dictionary, general sequences were rejected,
rule execution ignored focus/shape selection, and several CLI options differed.
The upstream bridge also aliases exception classes, so its passing result
cannot establish the public error contract. RDF report equality alone does not
measure report text, expanded graph interfaces, input mutation or full inference.

## Decision

Interpret the replacement target as preserving existing public imports, command
names, calls and observable behavior. The current `pyshacl_turbo` namespace
remains available for side-by-side comparison; unchanged `pyshacl` imports and
commands are explicitly unfinished. Reference and replacement distributions will
need isolated environments when implementing that shared namespace.

Keep five measurements separate: the corrected upstream suite, W3C conformance,
direct public contracts, code coverage, and performance. Never describe any
finite test percentage as universal compatibility. Export presence is an
availability check, not a behavioral test of that class. Unmeasured features
remain visible, including remote SPARQL, the HTTP server and SHACL-JS.

Run direct comparisons without the upstream bridge or its exception aliases.
Use fresh processes with bounded timeouts, and ADR 0006's safe macOS process
launcher. Record unexpected reference errors, timeouts and crashes separately;
none counts as a compatibility pass. This catches the pinned reference's empty
document autodetection hang and RDF/XML rule-output wrapper error without
making Turbo reproduce either failure.

Compare complete RDF structure, graph scope and blank-node sharing; normalize
only generated blank-node labels. Compare public result structure, text,
exceptions, warnings and mutations. Preserve generalized RDF in the comparison
representation so literal-subject inference triples cannot disappear from the
measurement. Keep the raw observations and timings in JSON.

Only publish a direct-call speedup when every measured observation agrees.
Rebuild inputs outside the timer, warm up once, retain every measured sample,
and require stable observations across repetitions. Keep the broader workload
matrix's report-parity and inference-closure distinctions explicit. Small-call
timings measure boundary overhead as well as native execution; Rust is not
assumed to win. CI gates correctness, not noisy timing thresholds.

Record the catalogue baseline in version control. CI requires its inventory
and rejects previously equal cases becoming different, as well as changed
failure states. Known differences remain reported as differences, not expected
passes. New differences require a regression before implementation changes.

## Implementation boundary

Rust applies focus and shape selection consistently during rule expansion and
validation, and produces the reference component/severity report headings.
Data-node descriptions use data namespaces; shape/path descriptions use shape
namespaces. Combining them changed default messages for Store inputs and for
graphs with different prefix bindings.
Python preserves the indexed multiple-input contract, public runtime-error
attributes, rule serialization contexts and CLI options. The runtime still
does not call pySHACL or owlrl. Native compiled shapes and Store inputs remain
additional capabilities.

The SPARQL-function native equivalent previously relied on the rule-selection
bug: it selected only the constraint shape but expected Jenny, whose target
class comes from a different rule shape, to be validated. Select that rule
shape explicitly as well. Both unbridged engines produce only Bob with the
constraint selected, and Bob plus Jenny with both shapes selected. The port's
two-focus-node, constraint-component and source-shape assertions are unchanged.

The intentional inference differences in ADR 0010 remain actual differences.
[ADR 0021](0021-standard-rdf-inference-output.md) resolves the generalized-RDF
portion of that decision: public output remains standard RDF, and literal-subject
reference statements are intentionally excluded. Raw observed differences remain
recorded. This does not waive valid-RDF differences or add a Python fallback.
