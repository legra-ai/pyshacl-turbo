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


def prepare(job, graph_observation):
    from rdflib import Graph

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

        def export():
            converted = source.to_rdflib()
            default = converted.default_graph.identifier
            if any(g != default for _, _, _, g in converted.quads()):
                raise RuntimeError("Closed fanout returned a non-default physical context")
            return converted.default_graph
    else:
        from owlrl import DeductiveClosure, OWLRL_Semantics

        source = Graph().parse(data=text, format="turtle")
        invoke = lambda: DeductiveClosure(OWLRL_Semantics).expand(source)
        export = lambda: source
    initial = facts(export())
    before_flags = flags(decimal.getcontext().flags)
    before_traps = flags(decimal.getcontext().traps)
    effects = {}

    def run():
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            warnings.catch_warnings(record=True) as records,
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            warnings.simplefilter("always")
            returned = invoke()
        effects.update(
            stdout=stdout.getvalue(),
            stderr=stderr.getvalue(),
            warnings=[
                {
                    "type": type(record.message).__module__ + "." + type(record.message).__name__,
                    "text": str(record.message),
                }
                for record in records
            ],
            returned_input=returned is source,
            returned_none=returned is None,
            return_type=type(returned).__module__ + "." + type(returned).__qualname__,
        )
        return source

    def observe(value):
        if value is not source or not effects:
            raise RuntimeError("Missing or foreign in-place fanout result")
        graph = export()
        complete = facts(graph)
        present = {json.dumps(row, sort_keys=True) for row in complete}
        if any(json.dumps(row, sort_keys=True) not in present for row in initial):
            raise RuntimeError("In-place inference changed an input fact or its literal cache")
        namespaces = [(prefix, str(name)) for prefix, name in source.namespaces()]
        return {
            "operation": "owlrl_inplace",
            "fixture": job["fixture"],
            "input_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "input_count": len(initial),
            "closure": graph_observation(graph),
            "complete_term_metadata": complete,
            "namespaces_raw": namespaces,
            "namespace_bindings": dict(namespaces),
            "public_effects": effects,
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
                "logical_scope": "default graph",
                "native_dataset_reference_graph_routes_are_distinct": True,
            },
        }

    return run, observe
