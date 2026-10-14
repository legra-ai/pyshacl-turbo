# ADR 0022: Preserve computed string terms and expose shape inspection

Status: Accepted

## Evidence

Differential rule-expansion tests found a term-identity mismatch: explicit
`"3"^^xsd:string` became plain `"3"`. ADR 0011
already preserved strings copied from input, but SPARQL datatype constructors
still canonicalized their results through `ExpressionTerm::StringLiteral`.
Reduced differential regressions reproduce this for `xsd:string`, `STRDT`,
and mixed `IF`/`COALESCE` branches. Blanket annotation of output strings would
incorrectly change `STR`, `CONCAT`, and existing plain terms.

Shape discovery and target evaluation existed in the native engine but were
not exposed through Python's shape inspection interfaces. Repeating data
conversion for every shape also introduced avoidable overhead.

## Decision

Extend spareval's existing opt-in exact-term evaluator to preserve datatype
constructor results. Preserve exact branch results even when sibling branches
use ordinary value expressions. Upstream default feature behavior is unchanged.
Do not globally annotate strings or repair terms at serialization time.

Expose `Shape` and `ShapesGraph` through matching modules in the `pyshacl_turbo`
namespace and as top-level exports. Discover shapes through the shared native
structural compiler. Evaluate focus nodes through the same Rust target evaluator
used by validation and rules; expose core targets before `set_advanced(True)`
and include advanced targets afterward. Deactivated shapes still expose their
targets, matching the reference's inspection API. Keep graph scope and caller
blank-node identities intact.

These classes implement inspection and targeting, not the reference's complete
validation/plugin interfaces. Unchanged `pyshacl` imports remain unfinished under
ADR 0020. Compilation is reused within a ShapesGraph instance. Each ordinary
Graph focus call takes a fresh data snapshot so graph mutations remain visible; repeated calls
still pay serialization and native parsing costs. Do not claim a speedup from
the implementation language or cache mutable input by object identity.

A local release-build check on Python 3.13.16/RDFLib 7.6.0 compared ten
`sh:targetClass` shapes over 1,000 typed subjects. After one warmup, five samples
for all ten calls were 5.001/4.489/4.491/4.462/4.602 ms for pySHACL and
203.342/192.368/190.580/203.395/180.679 ms for Turbo. Every target set matched.
This synthetic fixture exposes boundary overhead and gives no basis for
promising faster focus-node calls with ordinary Graph inputs. Reducing that overhead
requires a graph-access or explicitly reusable snapshot API, not an unsafe cache
of mutable RDFLib objects.

Expose `prepare_target_data(graph)` and its `TargetData` result as the explicit snapshot
API. Native parsing and construction of the default-union view happen once per
snapshot. `Shape.focus_nodes(snapshot)` caches immutable target sets keyed by
the compiled shape program, shape identity and advanced-mode setting. Return a
fresh Python set to callers. Failed evaluations are not cached. Keep caches owned
by the snapshot, with no global state or retention of the original mutable graph.

Reuse both the ShapesGraph and TargetData for a logical read of the source data.
Graph additions and removals become visible after explicitly preparing a new
snapshot. Passing an ordinary RDFLib graph still snapshots on every call and
therefore retains mutation visibility. This is an additional Turbo API; it does
not alter the meaning of existing pySHACL-compatible Graph calls. First-use costs
and repeated-use costs must be measured separately, including preparation in the
fresh-snapshot measurement. `benchmarks/targeting.py` retains raw samples and
source/native fingerprints and checks every target set against the reference.
The snapshot implementation's checked local samples are retained in
`benchmarks/targeting.json`; fresh and reused costs are both reported in the
README rather than presenting cached reads as fresh evaluations.

Describe package functionality in distribution metadata without maturity
classifiers. Report compatibility through measured behavior and documented
API support. Existing published artifacts retain their original metadata;
the next release carries this change.

## Validation

Differential Python regressions compare complete rule triples, target sets,
shape discovery and inspection with pySHACL 0.40.1. They cover Graph and Dataset
inputs, explicit literal and absent-node targets, subclass and implicit class
targets, subject/object targets, advanced SPARQL targets, deactivated shapes,
blank nodes and shape metadata. The full Python coverage gate and the standalone
spareval default/enabled-feature suites remain required.
