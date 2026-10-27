# ADR 0007: Preserve input-dependent pySHACL compatibility

Status: Accepted

## Evidence

The expanded suite exposes two distinctions omitted by the earlier narrow
milestone. pySHACL's closed constraint always ignores `(rdf:type, rdfs:Resource)`.
Also, pySHACL temporarily replaces RDFLib's boolean decoder while reading shapes
documents: lexical `"1"^^xsd:boolean` is false there, but true in an ordinary
caller-supplied Graph. A regression runs both input forms against the reference.
ADR 0003's boolean claim was based only on Graph inputs.

## Decision

Mirror both behaviors. Keep the original shapes graph for reports and SPARQL
shapes-graph access, but compile file-input SHACL boolean parameters with the
reference's lexical policy. Never modify RDFLib's process-wide decoding map.
Graph inputs retain their previous boolean behavior and W3C discrepancy.

For the public validate API, return `(False, ValidationFailure, text)` for SHACL
validation failures, matching pySHACL. Direct compilation and compiled-program
execution still raise immediately. This supersedes ADR 0004's public-API
exception difference. Other programming, unsupported-feature and shape errors
remain exceptions; no alternate engine runs after an error.

Public validation and rule expansion prepare caller-supplied shapes through
ShapesGraph before inference or target snapshots. Match the original's ordered
owl:Class/rdfs:Class and owl:DatatypeProperty/rdf:Property subclass additions,
including repeated add calls, selected contexts, aliases and Dataset union mode.
Parse data first: invalid data does not write shapes, while later inference or
shape errors retain these input-preparation writes. This also applies when an
explicit caller graph serves both input roles; it does not authorize committing
failed inference or rule deltas. Existing runner instances reuse their prepared
ShapesGraph. Explicit CompiledShapes remains an additional immutable API, and
implicit shapes do not bootstrap caller data. Preserve document-versus-Graph
boolean compilation policy and the native shapes capability path without copying
its dataset into RDFLib.
