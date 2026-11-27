# SHACL 1.2 Inference Rules acceptance

Implementation target: [10 November 2026 Working Draft](https://www.w3.org/TR/2026/WD-shacl12-inference-rules-20261110/).
This is an implementation acceptance contract, **not a claim of current support**.

Existing pySHACL-compatible entry points retain SHACL-AF semantics. Selecting
SHACL 1.2 inference must be explicit: its scheduling rules differ from AF.
A request for unsupported 1.2 execution must fail; it cannot silently execute AF.
The public invocation and native dependency will be added with the shared
executor, rather than defining an API against a nonexistent release.

The shared structural model describes rule declarations. The public
inference-engine owns portable scheduling and execution control. rdflib-turbo
owns concrete graph, query, target, condition and expression adapters;
pyshacl-turbo adapts the user-facing invocation and results. Adding a second
scheduler in either Python or the provider would create conflicting semantics.

## Pinned acceptance inputs

Use the original W3C data-shapes suite at
`0ed3f9b4273c2debba0125a7ed5c9dc3cd4b741c` (16 November 2026), already vendored
under `tests/w3c12`. `tests/suite-sources.json`, `LICENSE.md` and `SHA256SUMS`
retain its origin, license and exact files. No fixture rewriting is permitted.
The suite postdates the draft; any discrepancy requires explicit reconciliation,
not changing expected results until an implementation passes.

`tests/w3c_inference.py` loads Infer actions and grades an explicitly supplied
runner. It requires only inferred triples, checks exact graph isomorphism,
and verifies base and shapes graphs, including namespace bindings, remain
unchanged after success or failure. Only the adapter's declared execution failure
can satisfy `sht:Failure`; unrelated exceptions are errors. The runner is not yet
registered. Harness unit tests are not engine passes or conformance results.

Of 41 Infer cases, 40 currently have RDFLib-readable original inputs and results,
including six expected failures. `run-once-example` requires RDF 1.2 parsing.
Discovery-only lexical projections must never be executed. The separate Validate
cases exercising inference entailment also remain part of full acceptance.

## Execution requirements

| Capability | Pinned examples | Required behavior |
| --- | --- | --- |
| Global and shape rules | `global-symmetric`, `TripleRule-global`, `rectangle-simple` | Discover rules independently of shape links; bind focus only for shape rules. |
| Shared rule identity | `run-once-shared-shapes` | Union focus nodes across linked shapes; execute one run-once rule once per focus node. |
| Frozen phase visibility | `same-order`, `SPARQLRule-focus-nodes-isolated` | Same-order rules and all focus nodes of one execution observe the same phase. |
| Ordering and layers | `rule-order-visibility`, `layers-example`, `layers-decimal` | Compare exact numeric values; finish each layer's fixed point before the next layer. |
| Run-once phase | `run-once-blank-node-feed`, `run-once-example` | Run once before iterating rules; preserve fresh blank identity and termination behavior. |
| Conditions and deactivation | `condition-shape-class-superclass`, `deactivated-shape`, `rectangle-condition` | Apply all active conditions, including Shape/Class superclass constraints. |
| Expected predicates | `expectedPredicate-example`, `expectedPredicate-layers`, `expectedPredicate-also-inferred` | Compute derived triples before the layer; remove them afterward unless independently inferred. |
| Temporary triples | `temp-triples-example` | Remove temporary output and annotations at the specified lifecycle boundary. |
| Triple expressions | `TripleRule-cross-product`, `TripleRule-example-childCount`, `TripleRule-example-squares`, `TripleRule-skips-ill-formed` | Evaluate 1.2 node expressions, form Cartesian products and follow the specified invalid-triple handling. |
| SPARQL templates | `SPARQLRuleTemplate-example-Multiply`, `SPARQLRuleTemplate-optional-param`, `SPARQLRuleTemplate-missing-param` | Instantiate declared parameters, optional bindings and prefixes; missing required parameters fail. |
| Supported type selection | `multiple-rule-types`, `unknown-rule-type` | Execute a supported rule type when present; fail when no type is supported. |
| Processor selection | `ruleProcessor-unknown-at-rule`, `ruleProcessor-unknown-at-ruleset` | Unsupported required processors fail before output publication. |
| Entailment and rule sets | `rules-entailment-validation`, `rules-entailment-ruleset-includes`, `rdfs-domain-1` | Apply selected rule sets and inclusions in validation, preserving input scope. |
| Failure propagation | `TripleRule-failure`, `SPARQLRule-syntax-error` | Abort the attempt without caller-visible partial output. |

The concrete adapter also needs bounded or spilled staging and deduplication,
cancellation and configured execution limits. Graph-sized focus sets, run-once
keys, phase additions and provenance cannot be retained in unbounded controller
collections. Successful completion does not itself authorize promotion: caller
publication remains atomic and validates the original selected input snapshot.

## Completion gates

1. Reconcile shared declarations with the pinned draft, including exact schedule
   values and all executable constructs; model support alone is insufficient.
2. Implement and test the shared controller and concrete native adapters.
3. Add the explicit facade invocation and run every applicable Infer and
   inference-entailment Validate case through that actual public invocation.
4. Run existing pySHACL/AF compatibility gates and reconcile the single divergence
   ledger. Replace the typed not-run status only with measured execution results.
5. Verify the same built artifacts on supported platforms before publication.
