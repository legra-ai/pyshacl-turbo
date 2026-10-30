"""Closed literal-width cases consumed by the existing companion workers."""

import contextlib
import decimal
import hashlib
import io
import json
import struct
import warnings

PROFILES = ("literal-reflexivity", "literal-type")
WIDTHS = (32, 128, 512, 1000)


def fixture(width, profile):
    if profile not in PROFILES:
        raise ValueError(f"Unknown inference fanout profile: {profile}")
    if type(width) is not int or not 0 < width <= 1000:
        raise ValueError("Literal fanout width must be an integer in 1..1000")
    prefix = "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
    schema = (
        "<urn:membership:p> rdfs:range <urn:membership:Class> .\n"
        if profile == "literal-type"
        else ""
    )
    # bounded: at most1001 short synthetic statements, never user input.
    return (
        prefix
        + schema
        + "".join(f'<urn:membership:s{i}> <urn:membership:p> "value-{i}" .\n' for i in range(width))
    )


def cache(value):
    kind = type(value)
    if value is None or kind in (str, bool):
        payload = value
    elif kind is int:
        payload = str(value)
    elif kind is float:
        payload = struct.pack("!d", value).hex()
    elif kind is decimal.Decimal:
        parts = value.as_tuple()
        payload = [parts.sign, list(parts.digits), parts.exponent]
    else:
        raise RuntimeError(f"Unsupported cache in closed fanout observation: {kind}")
    return {"type": kind.__module__ + "." + kind.__qualname__, "value": payload}


def term(value):
    from rdflib import BNode, Literal, URIRef

    if not isinstance(value, (URIRef, BNode, Literal)) or len(str(value)) > 512:
        raise RuntimeError("Unsupported term in closed fanout observation")
    result = {"type": type(value).__name__, "word": str(value)}
    if isinstance(value, Literal):
        result.update(
            datatype=None if value.datatype is None else str(value.datatype),
            language=value.language,
            ill_typed=value.ill_typed,
            cache=cache(value.value),
        )
    return result


def facts(graph):
    # bounded: each closed synthetic fixture must finish below10000 output facts.
    result = []
    for subject, predicate, obj in graph:
        if len(result) == 10000:
            raise RuntimeError("Closed fanout output exceeded10000 facts")
        result.append([term(subject), term(predicate), term(obj)])
    return sorted(result, key=lambda row: json.dumps(row, sort_keys=True))


def flags(values):
    return {key.__name__: value for key, value in values.items()}


class CapturedCall:
    """Call-local streams/warnings, closed by observation or worker finally."""

    def __init__(self, source, invoke):
        self.source, self.invoke = source, invoke
        self.returned, self.called, self.closed = None, False, False
        self.stdout, self.stderr = io.StringIO(), io.StringIO()
        self.stack = contextlib.ExitStack()
        try:
            self.records = self.stack.enter_context(warnings.catch_warnings(record=True))
            self.stack.enter_context(contextlib.redirect_stdout(self.stdout))
            self.stack.enter_context(contextlib.redirect_stderr(self.stderr))
            warnings.simplefilter("always")
        except BaseException:
            self.close()
            raise

    def __call__(self):
        self.returned = self.invoke()
        self.called = True
        return self.source

    def close(self):
        if not self.closed:
            self.stack.close()
            self.closed = True

    def effects(self):
        if not self.closed or not self.called:
            raise RuntimeError("Capture must finish before observation encoding")
        return {
            "stdout": self.stdout.getvalue(),
            "stderr": self.stderr.getvalue(),
            "warnings": [
                {
                    "type": type(r.message).__module__ + "." + type(r.message).__name__,
                    "text": str(r.message),
                }
                for r in self.records
            ],
            "returned_input": self.returned is self.source,
            "returned_none": self.returned is None,
            "return_type": type(self.returned).__module__ + "." + type(self.returned).__qualname__,
        }


def prepare(job, graph_observation):
    from rdflib import Graph, URIRef

    backend = job["backend"]
    if backend not in {"reference", "turbo", "turbo_shared"} or job["operation"] != "owlrl":
        raise ValueError("Closed fanout requires an explicit OWL-RL reference/native route")
    text = fixture(job["nodes"], job["fixture"])
    native = backend != "reference"
    if native:
        from owlrl_turbo import expand
        from rdflib_turbo import Dataset

        source = Dataset().parse(data=text, format="turtle")
        invoke = lambda: expand(source, inference="owlrl", inplace=True)

        def export(*, inferred=False):
            converted = source.to_rdflib()
            default = converted.default_graph.identifier
            destination = URIRef("urn:owlrl-turbo:inference")
            allowed = {default, destination} if inferred else {default}
            graph = Graph()
            for s, p, o, context in converted.quads():
                if context not in allowed:
                    raise RuntimeError(
                        "Closed fanout returned an unexpected non-default physical context"
                    )
                graph.add((s, p, o))
            return graph, converted

        def physical_contexts(converted):
            default = converted.default_graph.identifier
            return sorted(
                [
                    {
                        "graph": None if graph.identifier == default else term(graph.identifier),
                        "facts": facts(graph),
                        "count": len(graph),
                    }
                    for graph in (
                        converted.graph(g) for g in {g for _, _, _, g in converted.quads()}
                    )
                    if len(graph)
                ],
                key=lambda row: json.dumps(row["graph"], sort_keys=True),
            )
    else:
        from owlrl import DeductiveClosure, OWLRL_Semantics

        source = Graph().parse(data=text, format="turtle")
        invoke = lambda: DeductiveClosure(OWLRL_Semantics).expand(source)
        export = lambda **kwargs: (source, source)
        physical_contexts = lambda converted: [
            {"graph": None, "facts": facts(source), "count": len(source)}
        ]
    initial = facts(export()[0])
    before_flags = flags(decimal.getcontext().flags)
    before_traps = flags(decimal.getcontext().traps)
    expected_type = type(source)

    def observe(value):
        call.close()
        if value is not source or not call.called or type(source) is not expected_type:
            raise RuntimeError("Missing or foreign in-place fanout result")
        if (native and call.returned is not source) or (not native and call.returned is not None):
            raise RuntimeError("Public in-place API returned an unexpected source/None value")
        graph, converted = export(inferred=True)
        contexts = physical_contexts(converted)
        default_facts = next((row["facts"] for row in contexts if row["graph"] is None), [])
        default_present = {json.dumps(row, sort_keys=True) for row in default_facts}
        if any(json.dumps(row, sort_keys=True) not in default_present for row in initial):
            raise RuntimeError(
                "In-place inference changed an input fact or its literal cache in the default graph"
            )
        complete = facts(graph)
        present = {json.dumps(row, sort_keys=True) for row in complete}
        if any(json.dumps(row, sort_keys=True) not in present for row in initial):
            raise RuntimeError("In-place inference changed an input fact or its literal cache")
        namespaces = [(prefix, str(name)) for prefix, name in source.namespaces()]
        return {
            "operation": "owlrl_inplace",
            "timed_boundary": "public invocation through call-local owner; capture setup, cleanup and all effect/RDF/cache/namespace/flag encoding outside timer",
            "fixture": job["fixture"],
            "input_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "input_count": len(initial),
            "closure": graph_observation(graph),
            "complete_term_metadata": complete,
            "physical_contexts": contexts,
            "initial_term_metadata": initial,
            "namespaces_raw": namespaces,
            "namespace_bindings": dict(namespaces),
            "public_effects": call.effects(),
            "decimal": {
                "flags_before": before_flags,
                "flags_after": flags(decimal.getcontext().flags),
                "traps_before": before_traps,
                "traps_after": flags(decimal.getcontext().traps),
            },
            "state": {
                "input_facts_preserved": True,
                "inplace": True,
                "container": type(source).__module__ + "." + type(source).__qualname__,
                "logical_scope": "complete closure",
                "native_dataset_reference_graph_routes_are_distinct": True,
            },
        }

    call = CapturedCall(source, invoke)
    try:
        return call, observe
    except BaseException:
        call.close()
        raise


def _namespace_authority(value):
    raw, bindings = value["namespaces_raw"], value["namespace_bindings"]
    if not isinstance(raw, (list, tuple)) or not isinstance(bindings, dict):
        raise TypeError("Malformed namespace authority")
    expected = {}
    for pair in raw:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise RuntimeError("Malformed namespace entry")
        prefix, name = pair
        if (
            not isinstance(prefix, str)
            or not isinstance(name, str)
            or not name
            or prefix in expected
        ):
            raise RuntimeError("Duplicate or malformed namespace binding")
        expected[prefix] = name
    if expected != bindings:
        raise RuntimeError("Namespace map does not match complete raw sequence")


def _projection(value, backend):
    required = {
        "operation",
        "fixture",
        "input_sha256",
        "input_count",
        "closure",
        "initial_term_metadata",
        "complete_term_metadata",
        "namespaces_raw",
        "namespace_bindings",
        "public_effects",
        "decimal",
        "state",
    }
    if not isinstance(value, dict) or not required <= value.keys():
        raise RuntimeError("Missing complete logical in-place observation")
    if value["operation"] != "owlrl_inplace" or value["fixture"] not in PROFILES:
        raise RuntimeError("Wrong closed inference operation/profile")
    count = value["input_count"]
    if type(count) is not int:
        raise RuntimeError("Invalid input fact count")
    width = count - (value["fixture"] == "literal-type")
    if (
        width not in WIDTHS
        or value["input_sha256"]
        != hashlib.sha256(fixture(width, value["fixture"]).encode()).hexdigest()
    ):
        raise RuntimeError("Wrong closed input hash/count")
    initial, complete, closure = (
        value["initial_term_metadata"],
        value["complete_term_metadata"],
        value["closure"],
    )
    if (
        not isinstance(initial, list)
        or not isinstance(complete, list)
        or len(initial) != count
        or not count <= len(complete) <= 10000
    ):
        raise RuntimeError("Missing bounded complete initial/output facts")
    if (
        not isinstance(closure, dict)
        or not {"ordinary", "full", "generalized_triples"} <= closure.keys()
    ):
        raise RuntimeError("Missing full/generalized closure")
    if closure["full"]["triples"] != len(complete):
        raise RuntimeError("Complete closure count differs from metadata rows")
    # bounded: at most10000 closed synthetic output rows; never an RDF data index.
    present = {json.dumps(row, sort_keys=True) for row in complete}
    if len(present) != len(complete) or any(
        json.dumps(row, sort_keys=True) not in present for row in initial
    ):
        raise RuntimeError("Duplicate output or lost initial fact/cache metadata")
    _namespace_authority(value)
    state, effects, context = value["state"], value["public_effects"], value["decimal"]
    if (
        not isinstance(state, dict)
        or not {"container", "inplace", "input_facts_preserved", "logical_scope"} <= state.keys()
    ):
        raise RuntimeError("Missing logical transition state")
    if (
        state["inplace"] is not True
        or state["input_facts_preserved"] is not True
        or state["logical_scope"] != "complete closure"
    ):
        raise RuntimeError("Invalid in-place logical transition")
    if (
        not isinstance(effects, dict)
        or not {"stdout", "stderr", "warnings", "return_type", "returned_none", "returned_input"}
        <= effects.keys()
    ):
        raise RuntimeError("Missing complete public effects")
    if (
        not isinstance(context, dict)
        or not {"flags_before", "flags_after", "traps_before", "traps_after"} <= context.keys()
    ):
        raise RuntimeError("Missing actual decimal flags/traps")
    if backend == "reference":
        valid = (
            state["container"] == "rdflib.graph.Graph"
            and effects["return_type"] == "builtins.NoneType"
            and effects["returned_none"] is True
            and effects["returned_input"] is False
        )
    elif backend in {"turbo", "turbo_shared"}:
        valid = (
            state["container"] in {"rdflib_turbo.Dataset", "rdflib_turbo.graph.StoreDataset"}
            and effects["return_type"] == state["container"]
            and effects["returned_none"] is False
            and effects["returned_input"] is True
        )
    else:
        raise RuntimeError("Unknown pinned benchmark route")
    if not valid:
        raise RuntimeError("Actual container/None/same-source return violates pinned route")
    # Shallow copies remove ONLY the four independently validated route fields.
    projected, projected_state, projected_effects = dict(value), dict(state), dict(effects)
    del projected_state["container"]
    for field in ("return_type", "returned_none", "returned_input"):
        del projected_effects[field]
    projected.update(state=projected_state, public_effects=projected_effects)
    return projected


def _stable_projection(run, backend):
    required = {
        "observation",
        "observations",
        "memory_samples",
        "samples_ns",
        "median_ns",
        "stable",
    }
    if not isinstance(run, dict) or not required <= run.keys():
        raise RuntimeError("Missing complete warm/cold measurement inventory")
    projected = _projection(run["observation"], backend)
    if (
        not run["samples_ns"]
        or len(run["observations"]) != len(run["samples_ns"]) + 1
        or not run["memory_samples"]
    ):
        raise RuntimeError("Missing warmup/timed/cold observations")
    values = [*run["observations"], *[sample["observation"] for sample in run["memory_samples"]]]
    for value in values:
        _projection(value, backend)
    return projected, run["stable"] is True and all(value == run["observation"] for value in values)


def logical_inplace_owlrl(left, right, *, left_backend, right_backend):
    """Scoped result only; raw full-API comparison remains entirely separate."""
    a, stable_a = _stable_projection(left, left_backend)
    b, stable_b = _stable_projection(right, right_backend)
    status = "logical_inplace_owlrl_"
    if not stable_a or not stable_b:
        return {"status": status + "unstable", "speedup": None}
    if a != b:
        return {"status": status + "different", "speedup": None}
    return {"status": status + "equal", "speedup": left["median_ns"] / right["median_ns"]}
