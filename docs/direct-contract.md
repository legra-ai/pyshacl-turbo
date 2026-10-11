# Direct pySHACL comparison

Reference: pySHACL 0.40.1. Turbo: 0.1.0.
Measured: 2026-10-11T17:40:02.622306+00:00; working-tree release build (see source and native binary hashes).
Platform: macOS-27.0.1-arm64-arm-64bit-Mach-O. Python: 3.13.16.
Source fingerprint: `886645896d5995ef763c3f560c289d49a5497f69a2f4d85326033b4767ec1b32`.

Each row calls the actual public package without the upstream test bridge.
RDF comparison preserves literal terms, graph scope and blank-node sharing;
generated blank-node labels are ignored. Report text and warning text are exact.
CLI RDF serialization is compared as RDF; usage banners compare their first error line.
Export presence checks measure availability only, not class behavior.

Timings are medians after an untimed warmup, excluding input construction and
observation encoding. Every timed repetition must match. Speedups are shown only
when all measured observations agree; they apply to these small fixtures only.
Reference errors/timeouts remain separate and never count as compatibility passes.

Outcomes: {'equal': 45, 'different': 15, 'reference_error': 1, 'reference_timeout': 1}. This catalogue is not universal compatibility coverage.

| Case | Outcome | Differences | Speedup |
| --- | --- | --- | --- |
| validate/graph/violation | equal |  | 0.68× |
| validate/graph/conforming | equal |  | 0.72× |
| validate/dataset/violation | equal |  | 0.57× |
| validate/dataset/conforming | equal |  | 0.42× |
| validate/store/violation | equal |  | 0.87× |
| validate/store/conforming | equal |  | 0.67× |
| validate/text/violation | equal |  | 0.83× |
| validate/text/conforming | equal |  | 1.22× |
| validate/bytes/violation | equal |  | 0.69× |
| validate/bytes/conforming | equal |  | 0.55× |
| validate/list | equal |  | 0.70× |
| validate_each/list | equal |  | 0.66× |
| validate/tuple | equal |  | 0.64× |
| validate_each/tuple | equal |  | 0.61× |
| validate/user-list | equal |  | 0.68× |
| validate_each/user-list | equal |  | 0.63× |
| validate_each/reject-empty-list | equal |  | — |
| validate_each/reject-graph | equal |  | — |
| validate_each/reject-text | equal |  | — |
| validate/legacy-positional | equal |  | 0.64× |
| validate_each/legacy-positional | equal |  | 0.65× |
| shacl_rules/legacy-positional | different | context_aware, identifier_type | — |
| validate/rules-focus | equal |  | 0.56× |
| shacl_rules/rules-focus | different | context_aware, identifier_type | — |
| validate/rules-shape | equal |  | 0.60× |
| shacl_rules/rules-shape | different | context_aware, identifier_type | — |
| validate/rules-untargeted | equal |  | 0.52× |
| shacl_rules/rules-untargeted | different | context_aware, identifier_type | — |
| validate/rules-override-target | equal |  | 0.48× |
| shacl_rules/rules-override-target | different | context_aware, identifier_type | — |
| shacl_rules/serialize-trig | equal |  | 0.86× |
| shacl_rules/serialize-turtle | equal |  | 0.69× |
| shacl_rules/serialize-nt | equal |  | 0.69× |
| shacl_rules/serialize-json-ld | equal |  | 0.52× |
| shacl_rules/serialize-xml | reference_error |  | — |
| inference/rdfs/complete-closure | different | mutation | — |
| inference/owlrl/complete-closure | different | mutation | — |
| inference/both/complete-closure | different | mutation | — |
| errors/shape-load | different | error | — |
| errors/constraint-load | different | error | — |
| errors/rule-load | different | error | — |
| reference/empty-document-autodetection | reference_timeout |  | — |
| exports/validate | equal |  | — |
| exports/validate_each | equal |  | — |
| exports/shacl_rules | equal |  | — |
| exports/Validator | different | present | — |
| exports/RuleExpandRunner | different | present | — |
| exports/Shape | different | present | — |
| exports/ShapesGraph | different | present | — |
| exports/__version__ | equal |  | — |
| cli/shapes-alias | equal |  | — |
| cli/allow-infos-alias | equal |  | — |
| cli/allow-warnings-alias | equal |  | — |
| cli/warning-short | equal |  | — |
| cli/max-depth | equal |  | — |
| cli/automatic-format | equal |  | — |
| cli/focus-whitespace | equal |  | — |
| cli/shape-whitespace | equal |  | — |
| cli/validate-each | equal |  | — |
| cli/rules-selection | equal |  | — |
| cli/no-input | equal |  | — |
| cli/missing-input | equal |  | — |
