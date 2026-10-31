"""Fresh-child sampling of the correctness-gated normal-policy Graph route."""

import contextlib
import decimal
import hashlib
import importlib.util
import io
import json
import statistics
import sys
import time
import warnings
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "matched_sampling_contract", Path(__file__).with_name("matched_graph_fanout.py")
)
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)
SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#> .
<urn:matched:shape> a sh:NodeShape; sh:targetSubjectsOf <urn:membership:p>;
 sh:property [ sh:path <urn:membership:p>; sh:minCount 1; sh:maxCount 1 ] ."""
POST_FIELDS = (
    "before",
    "after",
    "closure",
    "complete_term_metadata",
    "data_after_validation",
    "physical_contexts_after_validation",
    "report",
    "namespaces_raw",
    "effects",
    "warnings",
    "stdout",
    "stderr",
    "error",
)


def peak_rss():
    """Absolute process high-water mark; never subtract imports or setup."""
    import resource

    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return value
    if sys.platform == "linux":
        return value * 1024
    raise RuntimeError("Matched sampling supports Linux/macOS RSS units only")


def _clock():
    return time.perf_counter_ns(), time.process_time_ns()


def _elapsed(start, end):
    return {"wall_ns": end[0] - start[0], "cpu_ns": end[1] - start[1]}


def sample(backend, width, profile, expected):
    """Call once per fresh child, with a previously accepted complete oracle."""
    preparation_start = _clock()
    import rdflib
    from rdflib import Graph, URIRef

    if expected["before"]["normalize_literals"] is not True or expected.get("error") is not None:
        raise ValueError("Sampling requires an accepted normal=True correctness oracle")
    suite = CONTRACT._suite()
    text = suite.FANOUT.fixture(width, profile)
    if hashlib.sha256(text.encode()).hexdigest() != expected["input"]["sha256"]:
        raise ValueError("Sampling input differs from its correctness authority")
    factory, closure, semantics, validate, native = CONTRACT._products(backend)
    previous = rdflib.NORMALIZE_LITERALS
    rdflib.NORMALIZE_LITERALS = True
    stdout, stderr = io.StringIO(), io.StringIO()
    try:
        shapes = Graph(bind_namespaces="rdflib").parse(data=SHAPES, format="turtle")
        with decimal.localcontext(), warnings.catch_warnings(record=True) as records:
            warnings.simplefilter("always")
            before = CONTRACT._state()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                preparation_end = _clock()
                setup_peak = peak_rss()
                start = _clock()
                source = factory(identifier=URIRef("urn:matched:graph"), bind_namespaces="rdflib")
                owner = source.store
                native_owner = None if native is None else owner.backend._native
                parsed = source.parse(data=text, format="turtle")
                parsed_at = _clock()
                returned = closure(
                    semantics,
                    improved_datatypes=True,
                    rdfs_closure=False,
                    axiomatic_triples=False,
                    datatype_axioms=False,
                ).expand(source, destination=source)
                inferred_at = _clock()
                conforms, report, report_text = validate(
                    source,
                    shacl_graph=shapes,
                    inplace=True,
                    inference="none",
                )
                end = _clock()
                peak = peak_rss()
            # No scans, state dictionaries, exports, or observation serialization
            # occur between the three public operations or before the final RSS.
            after = CONTRACT._state()
            if type(source) is not factory or parsed is not source or returned is not None:
                raise RuntimeError("Public sampling factory/return contract failed")
            if (
                not isinstance(source, Graph)
                or type(conforms) is not bool
                or not isinstance(report, Graph)
            ):
                raise RuntimeError("Public sampling Graph/report contract failed")
            CONTRACT._owner(source, owner, native_owner)
            final = suite.FANOUT.facts(source)
            present = {json.dumps(row, sort_keys=True) for row in final}
            if any(
                json.dumps(row, sort_keys=True) not in present for row in expected["input"]["facts"]
            ):
                raise RuntimeError("Sample lost an initial fact or its exact literal authority")
            observation = {
                "before": before,
                "after": after,
                "closure": suite.graph_observation(source),
                "complete_term_metadata": final,
                "data_after_validation": final,
                "physical_contexts_after_validation": CONTRACT._physical_scopes(
                    source, factory, suite
                ),
                "report": {
                    "conforms": conforms,
                    "graph": suite.graph_observation(report),
                    "metadata_graph": CONTRACT._report_metadata(report, suite),
                    "text": report_text,
                    "namespaces_raw": [(p, str(v)) for p, v in report.namespaces()],
                },
                "namespaces_raw": [(p, str(v)) for p, v in source.namespaces()],
                "effects": {"inference_returned_none": True, "parse_returned_input": True},
                "warnings": [
                    {"type": CONTRACT._qualified(r.message), "text": str(r.message)}
                    for r in records
                ],
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "error": None,
                "diagnostics": {
                    "container": CONTRACT._qualified(source),
                    "store": CONTRACT._qualified(owner),
                    "native_handle": None
                    if native_owner is None
                    else CONTRACT._qualified(native_owner),
                    "source_id": id(source),
                    "store_id": id(owner),
                    "native_handle_id": None if native_owner is None else id(native_owner),
                    "data_owner_preserved": True,
                    "public_factory": factory.__module__ + "." + factory.__qualname__,
                },
            }
            oracle = {key: expected[key] for key in POST_FIELDS}
            oracle["diagnostics"] = expected["diagnostics"]
            # Correctness authorities and retained samples use JSON transport.
            # Roundtrip both sides at that boundary; preserve array order and
            # every lexical/cache/assessment/flag field without normalization.
            gate = CONTRACT.comparison(
                json.loads(json.dumps(oracle)), json.loads(json.dumps(observation))
            )
            return {
                "scope": "public Graph construction+parse; class closure construction+expand; public validate(inplace=True,inference=none); imports/text/SHAPES/captures prepared outside; no intermediate observation scans",
                "stages": {
                    "construct_parse": _elapsed(start, parsed_at),
                    "class_expand": _elapsed(parsed_at, inferred_at),
                    "validate": _elapsed(inferred_at, end),
                    "total": _elapsed(start, end),
                },
                "setup_peak_rss_bytes": setup_peak,
                "peak_rss_bytes": peak,
                "preparation": _elapsed(preparation_start, preparation_end),
                "gate": gate,
                "observation": observation,
                "intermediate_states": "No per-stage facts/cache/flags scans in sampled child; pinned correctness oracle establishes those boundaries separately",
            }
    finally:
        rdflib.NORMALIZE_LITERALS = previous


def summarize(reference, turbo):
    """Ratios require five complete, stable, equivalent samples per arm."""
    if len(reference) < 5 or len(turbo) < 5:
        raise ValueError("At least five retained fresh-child samples are required per arm")
    status = "equal"
    if any(value["gate"]["status"] != "equal" for value in reference + turbo):
        status = "different"
    if status == "equal":
        observations = [value["observation"] for value in reference + turbo]
        if any(CONTRACT.differences(observations[0], value) for value in observations[1:]):
            status = "different"
    if status != "equal":
        return {"status": status, "speedup": None, "rss_reduction": None}
    wall = [
        statistics.median(value["stages"]["total"]["wall_ns"] for value in arm)
        for arm in (reference, turbo)
    ]
    rss = [
        statistics.median(value["peak_rss_bytes"] for value in arm) for arm in (reference, turbo)
    ]
    return {
        "status": status,
        "speedup": wall[0] / wall[1],
        "rss_reduction": 1 - rss[1] / rss[0],
        "total_wall_median_ns": wall,
        "absolute_peak_rss_median_bytes": rss,
    }
