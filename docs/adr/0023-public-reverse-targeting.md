# ADR 0023: Public reverse targeting over immutable data snapshots

Status: Accepted

## Evidence

The forward inspection API exposes each shape's focus nodes. Determining the
active node shapes for one RDF term otherwise requires a loop over shapes,
with repeated target evaluation and membership checks. Prepared snapshots in
ADR 0022 establish an immutable lifetime for safely reusing these results.

Built distributions also omitted the inline typing marker, preventing static
tools from discovering the package's type information.

## Decision

Expose `CompiledShapes.targeting(data, node, skip=())` and the equivalent
`ShapesGraph.targeting` convenience method. Return a fresh list of RDFLib shape
identifiers sorted by N3 spelling. Include active node shapes with declared
targets; exclude property shapes, deactivated shapes and explicit exclusions.
The operation does not validate or follow constraint-dependent invocation paths.

Build the reverse index in Rust with the existing target evaluator. Supported
Core, implicit class and SHACL-AF targets retain their existing semantics.
Evaluate SPARQL queries normally and invert their complete results; prebinding
the requested node could change ORDER BY/LIMIT and aggregate semantics.

Cache the materialized index on TargetData by compiled program and exclusion
set. Excluded and inactive shapes are not evaluated. Failed evaluations propagate
without caching a partial result. Ordinary Graph inputs take a fresh snapshot
per call; prepared inputs retain ADR 0022's explicit refresh boundary.

Require RDFLib terms for the queried node and shape exclusions. Invalid arguments
raise TypeError rather than being treated as identifiers or expanded implicitly.
Literal focus nodes remain objects when transferring index entries across the
Python boundary, preserving standard RDF under ADR 0021.

Ship `py.typed` in source and wheel distributions. Package verification requires
the marker and installed-wheel smoke tests exercise reverse lookup without
pySHACL or owlrl installed.

## Validation

Differential tests use pySHACL 0.40.1 shape targeting with its target-type
registration initialized. Cases cover all Core target forms, subclass cycles,
implicit classes, parameterized SPARQL targets, ordering and LIMIT, named graphs,
blank shape identities, literal targets, exclusions, invalid arguments, failures,
snapshot refresh and independent compiled programs. Public documentation uses
synthetic data and executable examples.
