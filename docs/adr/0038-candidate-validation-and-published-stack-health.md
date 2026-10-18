# ADR 0038: Separate candidate validation from floating published-stack health

Status: Accepted

The shared-pipeline gate resolved the newest published package of each companion
before validating candidate wheels. Registry packages can embed different
canonical engines despite exposing the same protocol. That caused the latest
published baseline to fail identity checks before any candidate was exercised.
Blocking repaired candidates on that registry state creates a release deadlock.

Calls from tested-revision release CI and manual workflow runs explicitly select
candidate-releases.json: candidate wheels, the pinned reference and the pinned
historical baseline. Keep candidate integration tests, exact engine fingerprints,
full standard report comparisons, isolated installs and both host platforms as
mandatory gates. This is an upfront matrix selection, never a retry, conversion
fallback, swallowed error or continue-on-error path.

The independent weekly shared-pipeline workflow retains the complete releases.json
matrix and its floating latest-published environment. Its failures remain hard
failures with retained evidence. A scheduled parent release workflow supplies its
tested revision and uses the candidate gate; only the independent weekly workflow
has no revision input and probes the floating registry stack. Local users can
select either matrix explicitly. Reports preserve the entire selected matrix.

Do not claim that the published stack works when that monitor fails. Coordinating
package versions and source fingerprints remains release work; this decision
separates external registry health from the correctness of the proposed repair.
No package versions, public runtime protocols or benchmark report schema change.
