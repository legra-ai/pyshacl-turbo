"""Correctness-only matched public Graph route, separate from Dataset fanout."""

import contextlib
import decimal
import hashlib
import importlib.util
import io
import json
import warnings
from pathlib import Path


def _suite():
    path = Path(__file__).with_name("companions.py")
    spec = importlib.util.spec_from_file_location("matched_fanout_companions", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _qualified(value):
    return type(value).__module__ + "." + type(value).__qualname__


def _state():
    import rdflib

    context = decimal.getcontext()
    return {
        "normalize_literals": rdflib.NORMALIZE_LITERALS,
        "dawg_literal_collation": rdflib.DAWG_LITERAL_COLLATION,
        "decimal_flags": {key.__name__: val for key, val in context.flags.items()},
        "decimal_traps": {key.__name__: val for key, val in context.traps.items()},
        "decimal_precision": context.prec,
        "decimal_rounding": context.rounding,
    }


def _report_metadata(graph, suite):
    """Preserve full graph topology and cache-bearing literal occurrences."""
    from rdflib import Graph, Literal, URIRef

    decorated = Graph(bind_namespaces="none")
    tokens = {}
    # bounded: closed synthetic report, at most10000 triples.
    for index, triple in enumerate(graph):
        if index == 10000:
            raise RuntimeError("Matched report exceeds its closed observation budget")
        row = []
        for node in triple:
            if isinstance(node, Literal):
                encoded = json.dumps(suite.FANOUT.term(node), sort_keys=True, ensure_ascii=True)
                token = URIRef("urn:matched-cache:" + encoded.encode().hex())
                if json.loads(
                    bytes.fromhex(str(token)[len("urn:matched-cache:") :])
                ) != suite.FANOUT.term(node):
                    raise RuntimeError("Literal metadata token failed roundtrip")
                if token in tokens and tokens[token] != encoded:
                    raise RuntimeError("Literal metadata token collision")
                tokens[token] = encoded
                if any(token == item for source in graph for item in source):
                    raise RuntimeError("Literal token collides with an existing report term")
                row.append(token)
            else:
                row.append(node)
        decorated.add(tuple(row))
    return suite.graph_observation(decorated)


def _owner(source, owner, native_owner):
    if source.store is not owner or (
        native_owner is not None and owner.backend._native is not native_owner
    ):
        raise RuntimeError("The public pipeline replaced its DATA owner")


def _physical_scopes(source, factory, suite):
    # bounded: these fixtures have one intended source graph; retain extra graphs
    # as a real difference rather than substituting the requested scope for facts.
    result = []
    for context in source.store.contexts():
        identifier = getattr(context, "identifier", context)
        view = factory(store=source.store, identifier=identifier, bind_namespaces="none")
        result.append({"graph": suite.FANOUT.term(identifier), "facts": suite.FANOUT.facts(view)})
    return sorted(result, key=lambda row: json.dumps(row["graph"], sort_keys=True))


def _products(backend):
    from rdflib import Graph

    if backend == "reference":
        from owlrl import DeductiveClosure, OWLRL_Semantics
        from pyshacl import validate

        return Graph, DeductiveClosure, OWLRL_Semantics, validate, None
    if backend != "turbo":
        raise ValueError("Matched Graph requires reference or turbo backend")
    import owlrl_turbo._closure as closure
    import pyshacl_turbo
    from owlrl_turbo import DeductiveClosure, OWLRL_Semantics
    from rdflib_turbo import Graph as NativeGraph
    from rdflib_turbo import _native

    if closure.NativeGraph is not NativeGraph or closure.NativeStore is not _native.NativeStore:
        raise RuntimeError("OWL does not use the selected public Graph/native owner")
    if pyshacl_turbo._native.CompiledShapes is not _native.shacl.CompiledShapes:
        raise RuntimeError("SHACL does not use the selected native engine")
    if pyshacl_turbo._native._VALUE_COMPARISON_POLICY is not _native.shacl._VALUE_COMPARISON_POLICY:
        raise RuntimeError("SHACL/native comparison policy differs")
    return NativeGraph, DeductiveClosure, OWLRL_Semantics, pyshacl_turbo.validate, _native


def correctness(backend, width, profile, normalize):
    """Execute one fresh public pipeline; no timer or performance ratio."""
    import rdflib
    from rdflib import Graph, URIRef

    if type(normalize) is not bool:
        raise TypeError("The literal normalization scenario must be explicit")
    suite = _suite()
    text = suite.FANOUT.fixture(width, profile)
    factory, closure, semantics, validate, native = _products(backend)
    previous_policy = rdflib.NORMALIZE_LITERALS
    rdflib.NORMALIZE_LITERALS = normalize
    stdout, stderr = io.StringIO(), io.StringIO()
    result = {
        "operation": "matched_public_graph_pipeline",
        "scenario": "normalize-" + str(normalize),
    }
    source, owner, native_owner = None, None, None
    phase = "construct"
    try:
        with decimal.localcontext(), warnings.catch_warnings(record=True) as records:
            warnings.simplefilter("always")
            try:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    result["before"] = _state()
                    source = factory(
                        identifier=URIRef("urn:matched:graph"), bind_namespaces="rdflib"
                    )
                    if type(source) is not factory or not isinstance(source, Graph):
                        raise RuntimeError(
                            "Public factory did not return the selected Graph instance"
                        )
                    owner = source.store
                    if native is not None:
                        native_owner = owner.backend._native
                        if not isinstance(native_owner, native.NativeStore):
                            raise RuntimeError(
                                "Public Graph is not backed by the selected native store"
                            )
                    phase = "parse"
                    if source.parse(data=text, format="turtle") is not source:
                        raise RuntimeError("Public parse replaced its Graph")
                    _owner(source, owner, native_owner)
                    initial = suite.FANOUT.facts(source)
                    result["input"] = {
                        "sha256": hashlib.sha256(text.encode()).hexdigest(),
                        "facts": initial,
                    }
                    result["after_parse"] = _state()
                    shapes = Graph(bind_namespaces="rdflib").parse(
                        data="""@prefix sh: <http://www.w3.org/ns/shacl#> .
    <urn:matched:shape> a sh:NodeShape; sh:targetSubjectsOf <urn:membership:p>;
     sh:property [ sh:path <urn:membership:p>; sh:minCount 1; sh:maxCount 1 ] .""",
                        format="turtle",
                    )
                    phase = "inference"
                    returned = closure(
                        semantics,
                        improved_datatypes=True,
                        rdfs_closure=False,
                        axiomatic_triples=False,
                        datatype_axioms=False,
                    ).expand(source, destination=source)
                    if returned is not None:
                        raise RuntimeError("Class DeductiveClosure.expand did not return None")
                    _owner(source, owner, native_owner)
                    result["after_inference"] = _state()
                    inferred = suite.FANOUT.facts(source)
                    result["closure"] = suite.graph_observation(source)
                    result["complete_term_metadata"] = inferred
                    result["physical_contexts"] = _physical_scopes(source, factory, suite)
                    phase = "validation"
                    conforms, report, report_text = validate(
                        source,
                        shacl_graph=shapes,
                        inplace=True,
                        inference="none",
                    )
                    if type(conforms) is not bool or not isinstance(report, Graph):
                        raise RuntimeError("Public validation returned an invalid report")
                    _owner(source, owner, native_owner)
                    result["report"] = {
                        "conforms": conforms,
                        "graph": suite.graph_observation(report),
                        "metadata_graph": _report_metadata(report, suite),
                        "text": report_text,
                        "namespaces_raw": [(p, str(v)) for p, v in report.namespaces()],
                    }
                    phase = "observation"
                    final = suite.FANOUT.facts(source)
                    if initial != [row for row in final if row in initial] or inferred != final:
                        raise RuntimeError(
                            "Inference lost input authority or validation changed DATA"
                        )
                    result["data_after_validation"] = final
                    result["physical_contexts_after_validation"] = _physical_scopes(
                        source, factory, suite
                    )
                    result["namespaces_raw"] = [(p, str(v)) for p, v in source.namespaces()]
                    if source.store is not owner or (
                        native is not None and owner.backend._native is not native_owner
                    ):
                        raise RuntimeError("The public pipeline replaced its DATA owner")
                    result["diagnostics"] = {
                        "container": _qualified(source),
                        "store": _qualified(owner),
                        "native_handle": None if native_owner is None else _qualified(native_owner),
                        "source_id": id(source),
                        "store_id": id(owner),
                        "native_handle_id": None if native_owner is None else id(native_owner),
                        "data_owner_preserved": True,
                        "public_factory": factory.__module__ + "." + factory.__qualname__,
                    }
                    result["effects"] = {
                        "inference_returned_none": True,
                        "parse_returned_input": True,
                    }
            except (
                ArithmeticError,
                LookupError,
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as error:
                result["error"] = {
                    "phase": phase,
                    "type": _qualified(error),
                    "args": repr(error.args),
                    "text": str(error),
                }
            else:
                result["error"] = None
            result["after"] = _state()
            result["warnings"] = [
                {"type": _qualified(r.message), "text": str(r.message)} for r in records
            ]
    finally:
        result["stdout"], result["stderr"] = stdout.getvalue(), stderr.getvalue()
        rdflib.NORMALIZE_LITERALS = previous_policy
    return result


def differences(left, right):
    """Compare operation observables; retain nominal owner diagnostics separately."""
    if set(left) != set(right):
        return ["observation_fields"]
    # Nominal class/handle identities intentionally describe different implementations.
    return [key for key in left if key != "diagnostics" and left[key] != right[key]]


def comparison(left, right):
    """Keep mismatching/error cases visible without any performance claim."""
    different = differences(left, right)
    status = "different" if different else "equal"
    if left.get("error") is not None or right.get("error") is not None:
        status = "error"
    return {"status": status, "differences": different, "speedup": None, "rss_reduction": None}
