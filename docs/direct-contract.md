# Direct pySHACL comparison

Reference: pySHACL 0.40.2. Turbo: 0.10.2 with rdflib-turbo 0.2.0a39.
Measured: 2026-11-17T22:50:58.559792+00:00; installed shared native provider and pure Python facade.
Platform: macOS-27.0.1-arm64-arm-64bit-Mach-O. Python: 3.13.18.
Source fingerprint: `c2b3cc33bad8b0e0bc650f99a0842c13f62e880b1a63f8c619b119f471bc1aee`.

Each row calls the actual public package without the upstream test bridge.
RDF comparison preserves literal terms, graph scope and blank-node sharing;
generated blank-node labels are ignored. Report text and warning text are exact.
CLI RDF serialization is compared as RDF; usage banners compare their first error line.
Export presence checks measure availability only, not class behavior.

Timings are medians after an untimed warmup, excluding input construction and
observation encoding. Every timed repetition must match. Speedups are shown only
when all measured observations agree; they apply to these small fixtures only.
Reference errors/timeouts remain separate and never count as compatibility passes.

Outcomes: {'equal': 55, 'reference_error': 1, 'different': 5, 'reference_timeout': 1}. This catalogue is not universal compatibility coverage.
Every probe is first-party. Each non-equal case is an entry in the
[divergence ledger](../tests/divergences.toml); see ADR 0047.

| Case | Outcome | Differences | Ledger | Speedup |
| --- | --- | --- | --- | --- |
| validate/graph/violation | equal |  |  | 0.90× |
| validate/graph/conforming | equal |  |  | 0.93× |
| validate/dataset/violation | equal |  |  | 1.27× |
| validate/dataset/conforming | equal |  |  | 0.71× |
| validate/store/violation | equal |  |  | 0.72× |
| validate/store/conforming | equal |  |  | 1.18× |
| validate/text/violation | equal |  |  | 1.33× |
| validate/text/conforming | equal |  |  | 0.83× |
| validate/bytes/violation | equal |  |  | 0.96× |
| validate/bytes/conforming | equal |  |  | 0.23× |
| validate/list | equal |  |  | 0.94× |
| validate_each/list | equal |  |  | 0.93× |
| validate/tuple | equal |  |  | 1.10× |
| validate_each/tuple | equal |  |  | 4.56× |
| validate/user-list | equal |  |  | 1.04× |
| validate_each/user-list | equal |  |  | 1.02× |
| validate_each/reject-empty-list | equal |  |  | — |
| validate_each/reject-graph | equal |  |  | — |
| validate_each/reject-text | equal |  |  | — |
| validate/legacy-positional | equal |  |  | 0.87× |
| validate_each/legacy-positional | equal |  |  | 1.15× |
| shacl_rules/legacy-positional | equal |  |  | 0.74× |
| validate/rules-focus | equal |  |  | 0.85× |
| shacl_rules/rules-focus | equal |  |  | 0.52× |
| validate/rules-shape | equal |  |  | 0.67× |
| shacl_rules/rules-shape | equal |  |  | 0.42× |
| validate/rules-untargeted | equal |  |  | 0.60× |
| shacl_rules/rules-untargeted | equal |  |  | 0.61× |
| validate/rules-override-target | equal |  |  | 1.77× |
| shacl_rules/rules-override-target | equal |  |  | 0.45× |
| shacl_rules/serialize-trig | equal |  |  | 0.72× |
| shacl_rules/serialize-turtle | equal |  |  | 0.77× |
| shacl_rules/serialize-nt | equal |  |  | 0.81× |
| shacl_rules/serialize-json-ld | equal |  |  | 0.55× |
| shacl_rules/serialize-xml | reference_error |  | intentional | — |
| inference/rdfs/complete-closure | different | mutation | intentional | — |
| inference/owlrl/complete-closure | different | mutation | intentional | — |
| inference/both/complete-closure | different | mutation | intentional | — |
| errors/shape-load | equal |  |  | — |
| errors/constraint-load | different | error | gap | — |
| errors/rule-load | different | error | gap | — |
| reference/empty-document-autodetection | reference_timeout |  | intentional | — |
| exports/validate | equal |  |  | — |
| exports/validate_each | equal |  |  | — |
| exports/shacl_rules | equal |  |  | — |
| exports/Validator | equal |  |  | — |
| exports/RuleExpandRunner | equal |  |  | — |
| exports/Shape | equal |  |  | — |
| exports/ShapesGraph | equal |  |  | — |
| exports/__version__ | equal |  |  | — |
| cli/shapes-alias | equal |  |  | — |
| cli/allow-infos-alias | equal |  |  | — |
| cli/allow-warnings-alias | equal |  |  | — |
| cli/warning-short | equal |  |  | — |
| cli/max-depth | equal |  |  | — |
| cli/automatic-format | equal |  |  | — |
| cli/focus-whitespace | equal |  |  | — |
| cli/shape-whitespace | equal |  |  | — |
| cli/validate-each | equal |  |  | — |
| cli/rules-selection | equal |  |  | — |
| cli/no-input | equal |  |  | — |
| cli/missing-input | equal |  |  | — |
