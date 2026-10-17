# Versioned shared-dataset pipeline benchmarks

The [first measured shared-runtime report](releases-initial-run.md) and its
[compressed raw evidence](releases-initial-run.json.gz) retain the initial
candidate's exact source revisions, wheel identities and measurements. Current
CI reports use the candidate built from their recorded source pins.

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

## Continuous reports

The required `shared-pipeline` CI gate builds coordinated wheel sets and checks the
actual shared path on Linux and macOS, including regressions that prohibit dataset
copying/serialization/conversion while measuring the pipeline. Main-branch runs,
manual runs and the weekly schedule retain raw JSON, locks, wheel artifacts and a
Markdown report in GitHub Actions. Weekly runs also include 10,000 records.

Successful main runs append both platform reports to the generated
[`benchmark-results` history branch](https://github.com/legra-ai/pyshacl-turbo/tree/benchmark-results).
Its index links immutable reports, compressed raw evidence, dependency locks and
the originating workflow run. PRs cannot publish history. Coverage Pages are
independent of this history. Existing results are preserved; failed or incomplete
platform runs cannot update the public index.

Release order: merge/publish owlrl-turbo's compatible dependency range, then the
dataset-owning rdflib-turbo runtime, then the pyshacl-turbo facade. The source pins
allow all three candidate wheels to be tested together before those releases.
Future engine implementation changes require a coordinated runtime pin update;
the fingerprint deliberately prevents silently mixing different SHACL engines.
