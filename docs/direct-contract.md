# Direct pySHACL comparison

Reference: pySHACL 0.40.2. Turbo: 0.10.9 with rdflib-turbo 0.2.0a43.
Measured: 2026-11-28T09:34:49.874866+00:00; installed shared native provider and pure Python facade.
Platform: macOS-27.0.1-arm64-arm-64bit-Mach-O. Python: 3.15.2.
Source fingerprint: `94ce6c86fb4c64249c9f5c380c2943814b2e5efbe9ff4b7911542de0abc4c965`.

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
| validate/graph/violation | equal |  |  | 1.01× |
| validate/graph/conforming | equal |  |  | 0.83× |
| validate/dataset/violation | equal |  |  | 0.78× |
| validate/dataset/conforming | equal |  |  | 0.81× |
| validate/store/violation | equal |  |  | 1.09× |
| validate/store/conforming | equal |  |  | 0.87× |
| validate/text/violation | equal |  |  | 0.82× |
| validate/text/conforming | equal |  |  | 0.93× |
| validate/bytes/violation | equal |  |  | 0.80× |
| validate/bytes/conforming | equal |  |  | 0.83× |
| validate/list | equal |  |  | 0.95× |
| validate_each/list | equal |  |  | 0.89× |
| validate/tuple | equal |  |  | 1.02× |
| validate_each/tuple | equal |  |  | 1.04× |
| validate/user-list | equal |  |  | 0.93× |
| validate_each/user-list | equal |  |  | 0.99× |
| validate_each/reject-empty-list | equal |  |  | — |
| validate_each/reject-graph | equal |  |  | — |
| validate_each/reject-text | equal |  |  | — |
| validate/legacy-positional | equal |  |  | 0.95× |
| validate_each/legacy-positional | equal |  |  | 0.94× |
| shacl_rules/legacy-positional | equal |  |  | 0.61× |
| validate/rules-focus | equal |  |  | 0.81× |
| shacl_rules/rules-focus | equal |  |  | 0.67× |
| validate/rules-shape | equal |  |  | 0.75× |
| shacl_rules/rules-shape | equal |  |  | 0.69× |
| validate/rules-untargeted | equal |  |  | 0.62× |
| shacl_rules/rules-untargeted | equal |  |  | 0.49× |
| validate/rules-override-target | equal |  |  | 0.69× |
| shacl_rules/rules-override-target | equal |  |  | 0.50× |
| shacl_rules/serialize-trig | equal |  |  | 0.81× |
| shacl_rules/serialize-turtle | equal |  |  | 0.73× |
| shacl_rules/serialize-nt | equal |  |  | 0.71× |
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
