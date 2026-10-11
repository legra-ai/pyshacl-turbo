# Compatibility and remaining work

The public Python module is `pyshacl_turbo`. Runtime validation, rules, SPARQL,
report construction and inference execute in Rust. The pinned differential
reference is pySHACL 0.40.1. The goal is complete drop-in compatibility, including
SHACL-JS as future work. Current implementation work focuses on non-JS gaps.
See [ADR 0020](adr/0020-measure-the-complete-public-contract.md).

## Measurements

The [direct public-contract report](direct-contract.md) and
[raw observations](direct-contract.json) call both installed engines without
the upstream bridge. They compare API result structure, RDF graph scope, exact
report text, error attributes, warnings, mutations, CLI behavior and public
export availability. Timeouts and reference failures have their own outcomes.
The catalogue is an expanding set of probes, not an overall compatibility
percentage. Class availability is separate from class behavior.

Reproduce it with:

```sh
.venv/bin/python scripts/compare_contract.py --output direct-contract.json
```

CI checks the committed inventory and rejects regressions from equal cases.
It retains known differences as differences. Timings are diagnostic; they are
not CI speed thresholds. See the [workload benchmark](../benchmarks/drop-in.md)
for larger Core, rule, shape-count and SPARQL workloads.

The latest Turbo run passes **403/403 cases (100%)** in the locally corrected
upstream suite: 400 unchanged behavioral cases, one corrected fixture, and two
native equivalents. All cases must pass in CI.

The complete non-JS upstream suite contains 403 parametrized cases, including
functions in package initializers and nonstandard filenames. See
[upstream-coverage.json](upstream-coverage.json) for current case-level outcomes.
The test bridge blocks reference validation and rule execution. Both engines run
with upstream failure allowances disabled. Skips and collection errors never
count as passes.

Current report IDs use repository-relative fixture paths for parametrized cases.
Moving the checkout between macOS and Linux does not change the inventory;
fixture names, parameter values and native-equivalent mappings remain intact.

Two implementation-specific cases have explicit native equivalents, recorded in
the JSON. They verify native SPARQL function invocation and the Store adapter,
instead of a reference Python callback or wrapper class name. See
[ADR 0009](adr/0009-native-af-and-compatibility-audit.md).

The reference run passes 401/403 after the same fixture correction: two
`shapesGraph-001` variants fail after disabling upstream allowances. These
reference failures remain in [upstream-reference.json](upstream-reference.json).
Turbo passes the two shapesGraph cases. Reference failures are not relabeled as
Turbo passes.

The [local correction](../vendor/pyshacl-issue-70.patch) fixes `bad_test_070`'s
incorrect expectation that invalid geometry data conforms. It now asserts the
single missing-class violation, including its focus node, path and value, then
supplies `sf:Point rdfs:subClassOf geo:Geometry` and asserts conformance. Its
remote shapes are pinned to the audited immutable revision. The
[fixture audit](reference-fixture-audit.json) runs this actual corrected test
with both engines and requires isomorphic reports for both input states.
Both engines pass the corrected test. The report marks it with `local_correction`;
this is a locally corrected suite result, not a claim that the unmodified
upstream test now passes. The previous uncorrected Turbo result was 402/403.
See [ADR 0018](adr/0018-correct-upstream-geometry-fixture.md).

The pinned W3C suite now runs through both public input paths. Document inputs
pass **120/120 (100%)**: 98 Core and 22 SPARQL. RDFLib Graph inputs still pass
**119/120**: 97/98 Core and 22/22 SPARQL. The `uniqueLang-002` discrepancy remains
a strict expected failure for Graph input. pySHACL's document loader and ordinary
Graph input interpret the numeric boolean spelling differently; see ADR 0007.
The document run adds API coverage without changing engine semantics or the
original Graph measurement. Both runs compare report fields, result multiplicity
and paths. Graph inputs require exact input blank-node identity; document inputs
compare their descriptions and shared references across independent parses.
See [ADR 0014](adr/0014-complete-python-coverage.md). A finite passing suite does
not prove universal compatibility.

The complete Python package has **100% line and branch coverage**, enforced by
CI with no omitted package files. This measures executed Python API/CLI code,
not Rust coverage or universal SHACL compatibility. The coverage expansion found
and fixed N-Quads CLI report serialization, lost namespace bindings in combined
inputs, and acceptance of malformed DASH reports missing `sh:conforms`.

## Implemented

- All Core constraint families and all seven property-path forms.
- Count, length and qualified-count parameters use exact arbitrary-precision
  integers with the reference's separate datatype rules. Default messages,
  noncanonical integer forms and qualified empty-batch behavior have 141
  additional regressions; see [ADR 0016](adr/0016-exact-integer-parameters.md).
- Native Core pattern matching supports Python lookarounds, backreferences,
  conditionals, atomic groups, Unicode/ASCII modes and scoped flags. An additional
  82 regressions compare reports, syntax errors, reuse and mutation behavior;
  see [ADR 0013](adr/0013-native-python-patterns.md).
- SPARQL constraints, ASK/SELECT custom components, target queries, parameterized
  target types, prefix declarations and SHACL variable prebinding.
- Native SPARQL REGEX and REPLACE follow the pinned Python/RDFLib behavior,
  including Python constructs, replacement groups and empty matches. Native
  callbacks and query JSON preserve exact literal identity. Default min/max-count
  messages now agree with the reference. An additional 104 regression cases
  exercise these paths; see [ADR 0015](adr/0015-native-sparql-patterns.md).
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

- Existing applications still need to use `pyshacl_turbo` imports and
  `pyshacl-turbo` commands. The reference's public `Validator`, `RuleExpandRunner`,
  `Shape` and `ShapesGraph` classes are not yet available. Rule results expose
  RDFLib objects rather than the reference's DataGraph wrapper, with observable
  interface differences. Typed shape/constraint/rule load errors still differ.
- SHACL-JS is planned and has not been implemented or measured. It is part of
  the complete replacement target, separate from the current non-JS suite.

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
- Core and SPARQL patterns support Python constructs, but exhaustive parser/error
  parity and Unicode database alignment remain unproven. The native backtracking
  limit raises a hard error;
  Python 3.14 regex changes need a version-aware contract. Exhaustive XSD
  lexical-space and SHACL-AF expression coverage remain unproven.
  SPARQL REPLACE deliberately retains RDFLib 7.6.0's flag-as-count behavior;
  correcting that behavior requires a separate reference-version decision.
- Multiple custom parameter values produce all combinations; pySHACL chooses an
  arbitrary single value. Referenced cyclic blank-node descriptions are retained
  in report graphs rather than truncated at a fixed depth.
- Remote SPARQL endpoint inputs are unsupported. HTTP server behavior and
  the private workload from the motivating screenshot remain unverified or
  unsupported. A supported local Store is not a remote SPARQL endpoint.

All five published platform wheels, including Windows, pass installation and
public API/CLI smoke checks. See [release evidence](releasing.md#initial-publication-evidence--2026-10-11).
These checks do not establish full platform-specific compatibility.

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
A [new Core-only matrix](../benchmarks/pattern-core.md) measures the ADR 0013
pattern changes and retains complete report parity as a timing prerequisite.
The [SPARQL pattern matrix](../benchmarks/sparql-patterns.md) measures ADR 0015's
REGEX/REPLACE path, with equivalent typed-string inputs across RDFLib and Store
adapters. It also requires full report parity and records concurrent build load.
