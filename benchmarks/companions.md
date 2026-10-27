# Benchmarking the three companion turbo projects

One shared suite measures RDFLib versus rdflib-turbo, OWL-RL versus owlrl-turbo,
pySHACL versus pyshacl-turbo, and the complete parse → infer → convert → validate
pipeline. The other two repositories link here instead of maintaining copies of
the workload definitions. See [ADR 0031](../docs/adr/0031-companion-benchmarks.md).

Run serially on Linux or macOS, with Python 3.13 and uv available:

```sh
make benchmark-companions
```

This creates `benchmarks/.venv`, installs only published binary wheels from the
hash-pinned [uv lockfile](uv.lock), and writes
local `benchmarks/companions-current.json` and `.md` outputs. The checked-in
[first baseline report](companions-baseline-run.md) and its
[compressed raw JSON](companions-baseline-run.json.gz) retain the original evidence.
It does not use editable sibling checkouts. The first baseline pins
rdflib-turbo/owlrl-turbo 0.1.0a2 and pyshacl-turbo 0.2.4, alongside RDFLib 7.6.0,
OWL-RL 7.6.2 and pySHACL 0.40.1. These product versions remain historical fixtures;
Dependabot may update supporting utilities. Update the product requirements,
version matrices and recorded comparison deliberately when selecting a new baseline.
Do not mix local build
measurements into this published-artifact baseline.

For a smaller run after setup:

```sh
uv run --project benchmarks --locked --no-sync python -I benchmarks/companions.py \
    --nodes 100 --repeats 2 --memory-repeats 1 --output /tmp/companions.json
```

Use `--operations select owlrl pipeline_owlrl` to select phases. Sizes, repetition
counts and worker timeouts must be positive. Missing dependencies, worker crashes,
timeouts and failed conversion/mutation checks raise hard errors; partial evidence
is written to the requested output. There is no alternate backend or retry path.

The deterministic employee fixture has subclass and symmetric-property axioms,
cyclic relationships, integer scores and string names, with 10% missing names.
Sizes 100 and 1,000 contain 392 and 3,902 input statements. The named-graph variant
keeps schema statements in the default graph and records in a named graph.
Queries cover joins, filters, complete SELECT materialization, ASK, CONSTRUCT and
named-graph selection. Parsing covers Turtle and N-Quads; serialization covers
N-Triples and N-Quads. Inference covers RDFS and OWL-RL. Conversion measures both
directions and a round trip, with no invented reference speedup.

Each timing worker performs one warmup, then retains five measured samples.
Mutable inputs are rebuilt outside every timed call. Parsing, serialization,
query result materialization and public report construction are inside their
respective timers. Inference includes the default copy operation for both engines.
The pipeline starts from the same in-memory Turtle text, includes parsing,
in-place inference, the current native-to-RDFLib handoff and validation, and
returns the complete report. Shape parsing is outside that timer. Independent
phase measurements must not be summed into an estimate of end-to-end time.

Each memory sample uses another fresh process, with no warmup and one operation.
`ru_maxrss` is captured immediately afterward, before result comparison. The
reported peak includes interpreter, backend imports, fixture preparation and the
retained result. It is **whole-process peak RSS**, not allocated bytes or an
operation-only delta. Setup high-water marks are retained and never subtracted:
subtracting two peaks does not measure operation memory. Three independent memory
samples are retained by default. RSS units are converted from bytes on macOS and
KiB on Linux. Windows is explicitly unsupported by this memory harness.

Workers use the existing macOS `posix_spawn` launcher and bounded timeouts. They
run serially, with reproducibly shuffled backend order. Timings exclude process
startup, fixture construction, file I/O and observation encoding. Package versions,
native binary hashes, harness/lockfile hashes, platform and raw samples are
recorded. These synthetic cases are a baseline, not a confidence interval or a
prediction of production capacity.

Correctness comparisons retain exact RDF terms, complete graph structure,
dataset scope, blank-node sharing, duplicate query rows, unbound variables,
conformance, complete report graphs and report text. Only generated blank-node
labels and unordered RDF/SELECT iteration are canonicalized. Literal normalization
is disabled explicitly for RDFLib parsing. Generalized reference statements are
retained separately from ordinary RDF, following ADR 0021.

The report distinguishes full equality, ordinary-RDF equality with generalized
differences, report-graph equality with text differences, and unstable output.
Raw observations are retained for each timing and memory call. Full-output speedup
ratios require stable, completely equal observations; a matching report graph
alone never earns a ratio. A completed measurement is not a compatibility pass.
CI checks benchmark correctness without performance thresholds.

[The checked-in baseline](companions-baseline.json) records fingerprints of each
backend's RDF observations, including existing report-message differences; the
compressed raw evidence retains the original observations. The baseline checker
requires the complete operation inventory for each selected size, checks every
warm and cold observation, and prevents previously equal rows losing equality.
Report text is still retained in the raw evidence and gates full-output speedups;
its ordering is not used to classify RDF regressions. Any changed RDF baseline,
including an intentional correction, requires review and an explicit baseline
update. Merely completing a run does not pass this correctness gate.

## Literal fanout in version comparisons

Version comparisons also submit the closed `literal-reflexivity` and
`literal-type` profiles through these same workers, at widths32,128,512,1000.
The latter adds one common range class. Inputs use unique literal words, so the
width of a shared generalized membership prefix cannot hide behind repeated
integer scores. These rows time only the public in-place OWL-RL invocation
through a call-local owner. Stream/warning capture starts at the end of setup;
observation first restores it, then encodes the actual return and effects. The
worker also closes capture in a finally block across RSS reads, clock calls,
invocation and observation failures. Parsing, export and all RDF, cache, namespace,
return and decimal observation encoding remain outside the timer. Existing employee,
copy-by-default inference and full-pipeline cases retain their own boundaries.

The new bounded observations retain complete RDF/generalized facts, literal
cache metadata, public output/warnings, decimal state, raw namespace sequences,
binding maps, input preservation and actual return/container distinctions.
Different namespace sequence or public return state remains a difference even
when graph structure agrees. Native Dataset and reference Graph routes are
labeled separately; their physical containers are not asserted equivalent.
The raw full-API comparison and pipeline gate remain unchanged. A separately
named `logical_inplace_owlrl` column validates each route's Graph/None or native
Dataset/same-source contract, then excludes only `state.container` and the three
return fields from cross-route comparison. Every other field stays strict,
including raw namespace sequence and binding map, complete initial/output facts
and caches, public streams/warnings and decimal flags/traps. Duplicate or malformed
namespace maps fail. Every warm and cold raw observation must be stable before
this scoped ratio is allowed. This is logical transition equality, not full API
or physical container interchangeability; namespace order differences still deny
both ratios.

Unsupported observations and output bounds fail rather than truncate. Historical
`rdflib-v1` fingerprints are unchanged. Timings remain informational; the native
indexed-work regression is the deterministic check against fanout scans.

## First baseline findings

The historical correctness catalogue explicitly selects `--observation-encoder
rdflib-v1`, as its Make target and CI do. This retains the original fingerprint
format and immutable baseline. Versioned release comparisons use the scalable
`unique-anchors-v1` encoder instead; its complete-graph digests identify their
method. Encoder selection happens before execution, and unknown versions fail.

The [original macOS run](companions-baseline-run.md) contains five warm timing
samples and three cold RSS samples per backend for each of 32 cases. At 1,000
records, native Turtle parsing was 9.26× faster, SELECT 9.94× faster and CONSTRUCT
1.13× faster on these fixtures, with full observed equality. The tiny ASK case
primarily measures query-planning and Python boundary overhead.

The native-to-RDFLib handoff cost 26.6 ms for 3,902 input statements; a round trip
cost 36.8 ms. The complete OWL-RL pipeline peaked at 116.4 MiB for Turbo versus
56.1 MiB for the reference. Native inference itself also used more peak RSS on
this fixture. These whole-process figures do not isolate Rust allocations or
attribute the entire pipeline peak to conversion.

RDFS and OWL-RL closures matched on ordinary RDF at both sizes. The reference
also emitted generalized statements; therefore inference rows carry no full-output
speedup ratio. Validation-only report graphs matched, but pyshacl-turbo 0.2.4
formats anonymous source-shape literals differently in report text.

The complete pipeline exposed a separate namespace boundary: native parsing does
not currently extract prefix bindings. After conversion, Turbo reports use
`<urn:example:p0>` where the reference uses `ex:p0`, changing message literals in
the report graph as well as report text. A diagnostic binding only `ex` on the
converted graph made the complete report graphs isomorphic, confirming the cause;
that binding is not added to the measured pipeline. Ordinary inferred closures
already agree. Preserve these observations rather than treating the pipelines
as equivalent or publishing a ratio based only on conformance.

The next implementation work should address namespace/report fidelity and
measure the memory/copy costs at the shared-dataset boundary. The benchmark does
not yet establish which internal allocation dominates that peak.

Closed fanout jobs also record explicit `literal-inplace-owlrl-v1` observer
availability against actual resolved versions, lock and installed payload hashes.
The known a2/a2/0.2.4 stack is marked not measured before invocation only after
confirming its public Dataset namespace API is actually absent; its historical
pipeline jobs remain unchanged. No namespace observation is invented. Other
versions are not excluded by version number: a strict public-route preflight
must succeed, followed by the real worker's complete schema, return-state and
raw warm/cold stability checks before any comparison. Unknown contracts and
API/observation failures are hard errors, not post-error exclusions. Candidate
artifacts retain their candidate labels. The existing cross-package engine gate
runs first, and configured version pins are unchanged.
