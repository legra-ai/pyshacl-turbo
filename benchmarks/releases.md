# Versioned shared-dataset pipeline benchmarks

The [first measured shared-runtime report](releases-initial-run.md) and its
[compressed raw evidence](releases-initial-run.json.gz) retain the initial
candidate's exact source revisions, wheel identities and measurements. Current
CI reports use the candidate built from their recorded source pins.

The [inference memory report](inference-memory.md) retains the journaled-runtime
before/after comparison, phase heap profiles, process RSS, locks and raw evidence.

The canonical workload in `companions.py` now supports a native shared pipeline:

```python
from rdflib_turbo import Dataset
from owlrl_turbo import expand
from pyshacl_turbo import validate

data = Dataset().parse(data=turtle_text)
expand(data, inference="owlrl", inplace=True)
conforms, report, text = validate(data, shacl_graph=shapes)
```

Parsing, inference and ordinary validation retain one exact-term native dataset.
The SHACL engine executes inside the dataset-owning extension under a read lock.
Its protocol and engine-source fingerprint must match the Python facade. Active
SHACL rules use a staged working copy and commit only after complete success when
`inplace=True` is requested. Named-graph union views remain internal. This does not
claim that the entire process is allocation-free: shape compilation, evaluation
indexes, union views and the public report have their own allocations.

## Candidate validation and published-stack monitoring

Release CI explicitly selects [candidate-releases.json](candidate-releases.json):
the exact candidate wheels, the pinned Python reference, and the pinned historical
Turbo baseline. Candidate integration tests, canonical engine fingerprints and
complete report parity remain mandatory on both Linux and macOS. No failed
operation is retried through another backend.

The independent weekly run selects the full [releases.json](releases.json) matrix,
which also resolves the floating published stack. Its incompatible engines,
installation failures and worker errors remain hard failures with retained
reports. Manual runs and calls from tested-revision CI use the candidate matrix;
pass `--matrix benchmarks/releases.json` explicitly for a local published-stack
comparison.

Independently released packages can temporarily expose different canonical engine
sources. Treating that registry state as a prerequisite for candidate validation
would prevent a corrected candidate from passing and being published. Keeping the
published-stack health check separate avoids that release deadlock without
relaxing source identity, hiding its error or replacing its resolved versions.
Reports retain their selected matrix, so these two comparisons stay identifiable.

## Repeatable comparisons

The [matrix](releases.json) compares four separately locked uv environments:

1. Original RDFLib 7.6.0, OWL-RL 7.6.2 and pySHACL 0.40.1.
2. The historical turbo baseline: rdflib-turbo/owlrl-turbo 0.1.0a2 and
   pyshacl-turbo 0.2.4, including the old native-to-RDFLib handoff.
3. The latest compatible published turbo versions, resolved once into a retained
   uv lock. Their declared runtime capabilities select the shared or historical
   pipeline before timing. A failing shared call is never retried via conversion.
4. Exact candidate wheels built from coordinated source archives. Full source
   revisions are pinned in [runtime-sources.json](runtime-sources.json).

The wheel builder rejects tracked edits and untracked inputs before building.
It builds every source archive from a separate detached Git checkout, including
pyshacl-turbo, so ignored local artifacts cannot enter the build. Checkout
identities are checked again after building.

The historical/reference sets remain fixed; the latest-published set continuously
tracks release improvements. Add exact environment entries to the matrix to
compare any other release combinations. Every report records the actual package
versions, native binary hashes, wheel hashes, engine fingerprints, dependency
locks, harness hashes, source revisions and platform. Candidate wheel builds are
identified by bytes and source revision even when their development version equals
an existing PyPI version. They are not presented as that published artifact.

Build all three wheels using the same process as CI, then run:

```sh
uv run --no-project --python 3.13 python scripts/build_benchmark_wheels.py --output /tmp/turbo-pipeline-wheels
uv run --no-project --python 3.13 python benchmarks/releases.py \
  --candidate-wheels /tmp/turbo-pipeline-wheels --integration-tests integration \
  --nodes 100 1000 --repeats 7 --memory-repeats 3 \
  --output benchmark-artifacts/releases.json
```

Use a fresh output directory for each run. Without `--candidate-wheels`, candidate
versions resolve from PyPI using the declared matrix requirements. Missing wheels,
incompatible engine fingerprints, failed workers, timeouts and ordinary-RDF/report
graph regressions are hard failures. Partial evidence is retained; failed runs
cannot replace successful published measurements.

## What is measured

The timer covers parsing the same in-memory RDF text, in-place RDFS or OWL-RL
inference, SHACL shape compilation through the public API and construction of the
complete public report. Shape-document parsing and fixture generation happen
outside the timer. Public API caches warm naturally. The historical pipeline
also includes its conversion cost. Full inferred closures and complete reports
are compared after timing; their encoding is excluded from timings and RSS.

Each environment runs in serial fresh workers, with reproducibly shuffled order.
One warmup precedes seven retained timing samples. Reports include every sample,
median, minimum and maximum. Three independent cold workers measure one operation
each, capturing whole-process peak RSS before observation encoding. Peak RSS
includes interpreter, imports, fixtures, engine code, native/RDFLib state and the
retained report. Setup high-water marks are retained and never subtracted.
All builds, installations and integration tests finish before any measurement.

Full-output speedup ratios require stable, completely equal observations. Raw
generalized-RDF inference differences remain visible. Anonymous shape rendering
can still differ in report text; matching conformance or report graphs alone
does not earn a full-output speedup. The shared candidate must preserve the
ordinary RDF closure and complete report graph. Known historical differences
remain differences. These synthetic fixtures and shared CI runners provide
descriptive comparisons, not universal performance claims or precise production
capacity predictions; CI does not impose noisy timing thresholds.

Correctness encoding preserves every triple and blank-node link. When each blank
node has a unique label-independent local structural signature, those signatures
provide a canonical bijection directly. Ambiguous graphs use RDFLib's general
canonicalizer. The raw digest records the encoding method, and the harness hash
identifies its implementation. Compare output digests with the same encoder;
older report hashes are not interchangeable across harness changes. Encoding
remains outside both the operation timer and captured peak RSS.

## Continuous reports

The required `shared-pipeline` CI gate builds coordinated wheel sets and checks the
actual shared path on Linux and macOS, including regressions that prohibit dataset
copying/serialization/conversion while measuring the pipeline. Main-branch runs,
manual runs and the weekly schedule retain raw JSON, locks, wheel artifacts and a
Markdown report in GitHub Actions. Weekly runs also include 10,000 records.
Those larger workers have an explicit 900-second budget, including repeated
full-output encoding; ordinary 100/1,000-record CI workers retain 180 seconds.

Successful main runs append both platform reports to the generated
[`benchmark-results` history branch](https://github.com/legra-ai/pyshacl-turbo/tree/benchmark-results).
Its index links immutable reports, compressed raw evidence, dependency locks and
the originating workflow run. PRs cannot publish history. Coverage Pages are
independent of this history. Existing results are preserved; failed or incomplete
platform runs cannot update the public index.

Every branch requires signed commits. The owner initializes the artifact-only
branch once with `uv run --no-project python scripts/init_benchmark_history.py`,
using the existing Git signing identity and an isolated index. CI then appends
GitHub-signed commits with an exact-parent check; no signing secret, unsigned
push, source-tree copying, or workflow-file write permission is needed.

Release order: merge/publish owlrl-turbo's compatible dependency range, then the
dataset-owning rdflib-turbo runtime, then the pyshacl-turbo facade. The source pins
allow all three candidate wheels to be tested together before those releases.
Future engine implementation changes require a coordinated runtime pin update;
the fingerprint deliberately prevents silently mixing different SHACL engines.
