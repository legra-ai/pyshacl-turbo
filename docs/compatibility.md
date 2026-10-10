# Compatibility and remaining work

The public Python module is `pyshacl_turbo`. Runtime validation, rules, SPARQL,
report construction and inference execute in Rust. The pinned differential
reference is pySHACL 0.40.1. SHACL-JS is excluded from this project's target.

## Measurements

The latest Turbo run passes **402/403 cases (99.8%)**: 400 unchanged behavioral
cases plus two native equivalents. One audited reference assertion fails.

The complete non-JS upstream suite contains 403 parametrized cases, including
functions in package initializers and nonstandard filenames. See
[upstream-coverage.json](upstream-coverage.json) for current case-level outcomes.
The test bridge blocks reference validation and rule execution. Both engines run
with upstream failure allowances disabled. Skips and collection errors never
count as passes.

Two implementation-specific cases have explicit native equivalents, recorded in
the JSON. They verify native SPARQL function invocation and the Store adapter,
instead of a reference Python callback or wrapper class name. See
[ADR 0009](adr/0009-native-af-and-compatibility-audit.md).

The strict reference run passes 400/403: `bad_test_070` fails its remote fixture
assertion, and two `shapesGraph-001` variants fail after disabling upstream
allowances. These reference failures remain in the inventory. Turbo passes the
two shapesGraph cases. Reference failures are not relabeled as Turbo passes.

The [immutable fixture audit](reference-fixture-audit.json) confirms that
`bad_test_070` now produces isomorphic nonconforming reports in both engines:
its geometry node lacks the required `geo:Geometry` class. The fixture's
`assert conforms` is wrong for the supplied data and shapes. It remains a strict
upstream failure; the audit does not turn it into a pass.

The separate pinned W3C run passes 119/120: 97/98 Core and 22/22 SPARQL. The
`uniqueLang-002` discrepancy is retained as a strict expected failure for RDFLib
Graph input. pySHACL's document loader and ordinary Graph input interpret the
numeric boolean spelling differently; see ADR 0007. A finite passing suite does
not prove universal compatibility.

## Implemented

- All Core constraint families and all seven property-path forms.
- SPARQL constraints, ASK/SELECT custom components, target queries, parameterized
  target types, prefix declarations and SHACL variable prebinding.
- SPARQLRules and TripleRules, ordering, conditions and bounded iteration.
- Native ASK/SELECT functions, nested node expressions, function argument products,
  paths, union, intersection and filterShape; expression constraints.
- Native RDFS/OWL-RL inference and selective ontology inoculation. No runtime
  owlrl or reference-validator dependency.
- RDFLib Graph/Dataset and optional PyOxigraph Store inputs, including named
  graphs. Rust callers can supply an oxigraph::Store directly.
- Paths, URLs, files, text and bytes; Turtle, TriG, N-Triples, N-Quads, RDF/XML, N3
  and JSON-LD boundary formats; imports, Meta-SHACL, focus/shape selection,
  severity options, multiple input graphs, report serialization and CLI tools.
- Stable human-readable reports, blank-node descriptions and namespace bindings.
- Exact plain-string versus explicit xsd:string identity for RDFLib and document
  inputs, including Core comparisons, cardinality, SPARQL sameTerm and rule output.
  Store strings retain their adapter's explicit xsd:string identity.
- Dataset, document and Store inference in `urn:pyshacl:inference`. Blank-node
  descriptions retain source graph scope; RDF reports still include inference.
- Reference constraint-path recursion warnings and skipped recursive edges,
  including rule conditions; configurable validation depth (default 15).
  Undefined scalar functions follow SPARQL expression-error semantics. Registered
  SHACL callback errors still propagate. See [ADR 0012](adr/0012-reference-recursion-and-expression-errors.md).
- Native datatype and annotation axioms, datatype subsumption and combined-mode
  RDFS/OWL bindings. Complete inferred-graph comparisons now pass for 21 local
  cases without generalized RDF, covering all three inference modes. Native
  key matching preserves blank-node class identity and checks every key property.

Imported parameter declarations with `sh:node` annotations no longer become
executable shapes solely because of those annotations. Explicit targets, shape
types and incoming shape references still require a supported validator.
The upstream DASH import regression now passes; see
[ADR 0010](adr/0010-parameter-roles-and-native-inference.md).

Store input uses native N-Quads across the independent Python extensions, without
an intermediate RDFLib data graph. It is a copy. The direct Rust Store API copies
quads without RDF text. Store commits add only newly derived quads, atomically,
after successful execution. They do not replay the original snapshot over
concurrent deletions. Neither path introduces Tokio or asynchronous I/O.

## Known limits

- Report formatting is substantially closer but not byte-for-byte identical.
  The upstream blank-node description case and issue 286 now pass; see
  [ADR 0011](adr/0011-literal-identity-and-report-graph-scope.md).
- Native inference does not yet reproduce the reference's complete closure.
  Some reference closure triples also use literal subjects, which RDF datasets
  cannot represent. See the measured inference differences in the benchmark.
  Native keys require a common value for every key property; the pinned reference
  reasoner omits the last property from its comparison. Turbo does not reproduce
  that incorrect identity inference. Empty key lists are inactive in both.
  Benchmarks compare ordinary RDF and generalized triples separately; a matching
  ordinary portion never counts as a matching complete closure.
  The current RDFS and OWL-RL cases match on all ordinary RDF triples. The
  reference additionally produces 901 and 902 literal-subject triples respectively
  on the 1,000-node cases, so both full-closure comparisons still fail.
- Regex uses Rust syntax; Python-only lookaround/backreferences are rejected.
  Exhaustive XSD lexical-space and SHACL-AF expression coverage remain unproven.
- Multiple custom parameter values produce all combinations; pySHACL chooses an
  arbitrary single value. Referenced cyclic blank-node descriptions are retained
  in report graphs rather than truncated at a fixed depth.
- Remote SPARQL endpoint inputs, HTTP server behavior, Windows wheels and
  the private workload from the motivating screenshot remain unverified or
  unsupported. A supported local Store is not a remote SPARQL endpoint.

Performance is workload-specific. The matrix includes input transfer, report
construction, shape reuse, reasoning and both RDFLib and Store baselines. Full
validation report parity gates every timed path. Inference speedups are
provisional wherever complete inferred graphs differ. Raw samples and source
hashes identify the exact measured checkpoint.
The [current performance report](../benchmarks/current.md) also compares
the ordinary RDF portion separately, while retaining the full-closure failure
when generalized triples differ. This diagnostic never counts as full parity.
The matrix predates ADR 0012's recursion and undefined-function changes; source
hashes identify its measured checkpoint.
