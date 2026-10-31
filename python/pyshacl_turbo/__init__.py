"""pySHACL compatibility layer. All SHACL execution happens in Rust."""

import json
import logging
import sys
import warnings
from collections.abc import Iterable, Sequence
from dataclasses import replace
from functools import lru_cache, wraps
from importlib.metadata import version
from pathlib import Path

from rdflib import BNode, Dataset, Graph, Literal, URIRef

from . import _native
from ._inference import inference_mode
from .errors import (
    ConstraintLoadError,
    ReportableRuntimeError,
    ShapeLoadError,
    ShapeRecursionWarning,
    ValidationWarning,
)
from .graph_abstraction import DataGraph, _reject_native_store_graph
from .rdf import (
    Input,
    commit_serialized,
    is_oxigraph_store,
    load_from_source,
    merge_graph,
    shape_batches,
    shape_graphs,
    union,
)
from .rdf import decode as _graph
from .rdf import input_graph as _input
from .rule_expand_runner import RuleExpandRunner
from .shape import Shape
from .shapes_graph import ShapesGraph
from .target_data import TargetData, prepare_target_data
from .validator import Validator

ValidationFailure = _native.ValidationFailure
__version__ = version("pyshacl-turbo")
SHARED_DATASET_PROTOCOL = 1


def _shared_runtime(data):
    runtime = sys.modules.get("rdflib_turbo")
    if runtime is not None and (
        isinstance(data, runtime.Dataset)
        or callable(getattr(data, "_validate_shared_shapes", None))
    ):
        return runtime
    return None


def _check_rule_output(runtime, source, result, inplace):
    while isinstance(source, DataGraph):
        source = source._view
    if inplace:
        valid = result is source
    elif isinstance(source, runtime.Dataset):
        valid = isinstance(result, runtime.Dataset)
    elif isinstance(source, runtime.Graph):
        valid = isinstance(result, runtime.Graph) and not isinstance(result, runtime.Dataset)
        if valid:
            valid = result.identifier == source.identifier
    elif isinstance(source, (runtime.Store, runtime.Transaction)):
        valid = isinstance(result, runtime.Store)
    else:
        valid = False
    if valid and not inplace:
        source_owner = source.store.backend if isinstance(source, Graph) else source
        result_owner = result.store.backend if isinstance(result, Graph) else result
        valid = result_owner._native is not source_owner._native
    if not valid:
        raise RuntimeError("Invalid native rule expansion result ownership or graph scope")


def _failure_result(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except ValidationFailure as failure:
            failure.message = str(failure)
            return False, failure, f"Validation Failure - {failure}"
        except (NotImplementedError, ReportableRuntimeError):
            raise
        except RuntimeError as error:
            raise ReportableRuntimeError(str(error)) from error

    return wrapped


__all__ = [
    "CompiledShapes",
    "ReportableRuntimeError",
    "RuleExpandRunner",
    "Shape",
    "ShapeRecursionWarning",
    "ShapesGraph",
    "TargetData",
    "ValidationFailure",
    "ValidationWarning",
    "Validator",
    "__version__",
    "compile_shapes",
    "evaluate_query_testcase",
    "extract_query_and_expected_result",
    "load_from_source",
    "meta_validate",
    "prepare_target_data",
    "shacl_rules",
    "validate",
    "validate_each",
]


@lru_cache(maxsize=128)
def _compile_native(source, advanced, numeric_booleans, namespaces):
    try:
        return (
            _native.CompiledShapes.from_input(
                source, advanced, numeric_booleans, list(namespaces), _policy=_native._REGEX_POLICY
            ),
            source,
        )
    except _native.ShapeLoadFailure as error:
        raise ShapeLoadError(*error.args) from error
    except _native.ConstraintLoadFailure as error:
        raise ConstraintLoadError(*error.args) from error


def _check_shared_engine(shared):
    if getattr(shared, "SHARED_SHACL_PROTOCOL", None) != 1:
        raise RuntimeError("rdflib-turbo does not implement shared SHACL protocol 1")
    if shared.SHACL_ENGINE_FINGERPRINT != _native.SHACL_ENGINE_FINGERPRINT:
        raise RuntimeError("rdflib-turbo and pyshacl-turbo have different SHACL engine sources")


def _compile_for_data(shacl_graph, data_graph, shacl_graph_format, advanced, *, rules=False):
    runtime = _shared_runtime(data_graph)
    if runtime is not None and (not rules or isinstance(data_graph, runtime.Dataset)):
        _check_shared_engine(runtime._native)
    return compile_shapes(shacl_graph, shacl_graph_format=shacl_graph_format, advanced=advanced)


def _document_source(data):
    return (
        not isinstance(data, (Graph, DataGraph, Input))
        and _shared_runtime(data) is None
        and not is_oxigraph_store(data)
    )


def _prepare_public_shapes(data, shapes, data_format, shapes_format, ontology, inference, imports):
    if _document_source(data):
        data = load_from_source(
            data,
            rdf_format=data_format,
            multigraph=ontology is not None or inference not in (None, "none"),
        )
    if isinstance(shapes, ShapesGraph):
        return data, shapes
    graph_input = isinstance(shapes, Graph)
    if callable(getattr(shapes, "_compile_shared_shapes", None)):
        if imports:
            raise NotImplementedError("Native shapes OWL imports are not implemented")
        graph = shapes
    else:
        _reject_native_store_graph(shapes)
        graph = load_from_source(shapes, rdf_format=shapes_format, do_owl_imports=imports)
    prepared = ShapesGraph(graph)
    prepared._numeric_booleans = graph_input
    return data, prepared


class CompiledShapes:
    """Reusable immutable shapes; native Dataset validation borrows its runtime."""

    def __init__(self, shacl_graph, *, shacl_graph_format=None, advanced=False):
        self._prepare(shacl_graph, shacl_graph_format, advanced)
        if self._native is None:
            source, advanced, namespaces, numeric_booleans = self._shared_spec
            self._native, source = _compile_native(source, advanced, numeric_booleans, namespaces)
            self._shared_spec = (source, advanced, namespaces, numeric_booleans)

    def _prepare(self, shacl_graph, shacl_graph_format, advanced):
        numeric_booleans = isinstance(shacl_graph, Graph)
        if isinstance(shacl_graph, ShapesGraph):
            numeric_booleans = shacl_graph._numeric_booleans
            shacl_graph = shacl_graph.graph
        compile_native = getattr(shacl_graph, "_compile_shared_shapes", None)
        if callable(compile_native):
            self.graph = shacl_graph
            self._blank_nodes = {}
            try:
                self._native, self._shape_namespaces = compile_native(advanced)
            except _native.ShapeLoadFailure as error:
                raise ShapeLoadError(*error.args) from error
            except _native.ConstraintLoadFailure as error:
                raise ConstraintLoadError(*error.args) from error
            self._shared_spec = None
            self._shared_program = None
            return
        _reject_native_store_graph(shacl_graph)
        self.graph = load_from_source(shacl_graph, rdf_format=shacl_graph_format)
        self._blank_nodes = {}
        source = _native.ShapesInput(
            shape_batches(self.graph, self._blank_nodes),
            self.graph.context_aware,
            shape_graphs(self.graph, self._blank_nodes),
        )
        namespaces = tuple((p, str(ns)) for p, ns in self.graph.namespaces())
        self._shape_namespaces = namespaces
        self._native = None
        self._shared_spec = (
            source,
            advanced,
            namespaces,
            numeric_booleans,
        )
        self._shared_program = None

    def targeting(
        self,
        data_graph,
        node: URIRef | BNode | Literal,
        *,
        skip: Iterable[URIRef | BNode] = (),
    ) -> list[URIRef | BNode]:
        """Return active node-shape identifiers whose declared targets include node.

        Reuse TargetData to share a native reverse index across node lookups.
        Excluded shapes are not evaluated. Graph inputs read fresh data per call.
        """
        return prepare_target_data(data_graph)._targeting(self, node, skip)

    def validate(
        self,
        data_graph,
        *,
        data_graph_format=None,
        inplace=False,
        inference=None,
        iterate_rules=False,
        max_rule_iterations=100,
        max_validation_depth=15,
        allow_infos=False,
        allow_warnings=False,
        abort_on_first=False,
        focus_nodes=None,
        use_shapes=None,
        _normalize_report_literals=None,
    ):
        runtime = _shared_runtime(data_graph)
        if runtime is not None:
            if data_graph_format is not None:
                raise ValueError("data_graph_format is unavailable for a native source")
            from rdflib_turbo import _native as shared

            _check_shared_engine(shared)
            if self._shared_program is None:
                self._shared_program = shared.SharedShapes.from_compiled(
                    self._native, _comparison_policy=_native._VALUE_COMPARISON_POLICY
                )
            execute = getattr(data_graph, "_validate_shared_shapes", None)
            if not callable(execute):
                raise RuntimeError("Native source does not implement borrowed SHACL validation")
            data_namespaces = (
                dict(data_graph.namespaces())
                if isinstance(data_graph, (runtime.Dataset, Graph))
                else dict(self._shape_namespaces)
            )
            inference = inference_mode(inference)
            settings = {
                "iterate_rules": iterate_rules,
                "max_rule_iterations": max_rule_iterations,
                "max_validation_depth": 15
                if max_validation_depth is None
                else max_validation_depth,
                "allow_infos": allow_infos,
                "allow_warnings": allow_warnings,
                "abort_on_first": abort_on_first,
                "focus_nodes": _expand_names(data_namespaces, focus_nodes),
                "use_shapes": _expand_names(dict(self._shape_namespaces), use_shapes),
            }
            if inference not in (None, "none"):
                settings["inference"] = inference
            try:
                with execute(self._shared_program, json.dumps(settings), inplace) as result:
                    conforms, report, text, recursion_warnings = result
                    if type(conforms) is not bool:
                        raise TypeError("Native report conformance must be a boolean")
                    _emit_recursion_warnings(recursion_warnings)
                    report_graph = _graph(
                        report,
                        self._blank_nodes,
                        preserve_ids=True,
                        report=True,
                        normalize=_normalize_report_literals,
                        _report_conforms=conforms,
                    )
                    for prefix, namespace in self._shape_namespaces:
                        report_graph.bind(prefix, namespace)
            except shared.SharedValidationFailure as failure:
                raise ValidationFailure(str(failure)) from failure
            return conforms, report_graph, text
        inference = inference_mode(inference)
        if inference not in (None, "none"):
            raise NotImplementedError(
                "CompiledShapes.validate pre-inference requires a native source; use validate for serialized inputs"
            )
        if inplace and not (
            isinstance(data_graph, (Graph, Input)) or is_oxigraph_store(data_graph)
        ):
            raise TypeError("inplace=True requires an RDFLib Graph or pyoxigraph Store")
        data = _input(data_graph, data_graph_format, direct=True)
        conforms, report, text, expanded, recursion_warnings = self._native.validate(
            data.source,
            data.format,
            data.base,
            iterate_rules,
            max_rule_iterations,
            15 if max_validation_depth is None else max_validation_depth,
            inplace,
            allow_infos,
            allow_warnings,
            abort_on_first,
            _expand_names(data.namespaces or dict(self._shape_namespaces), focus_nodes),
            _expand_names(dict(self._shape_namespaces), use_shapes),
            [(p, str(ns)) for p, ns in data.namespaces.items()],
            _comparison_policy=_native._VALUE_COMPARISON_POLICY,
        )
        if type(conforms) is not bool:
            raise TypeError("Native report conformance must be a boolean")
        _emit_recursion_warnings(recursion_warnings)
        nodes = self._blank_nodes | data.blank_nodes
        report_graph = _graph(
            report,
            nodes,
            preserve_ids=True,
            report=True,
            normalize=_normalize_report_literals,
            _report_conforms=conforms,
        )
        for prefix, namespace in self._shape_namespaces:
            report_graph.bind(prefix, namespace)
        if inplace:
            commit_serialized(data_graph, expanded, nodes, before=data)
        return conforms, report_graph, text

    def shacl_rules(
        self,
        data_graph,
        *,
        data_graph_format=None,
        inplace=False,
        iterate_rules=False,
        max_rule_iterations=100,
        max_validation_depth=15,
        focus_nodes=None,
        use_shapes=None,
        _return_dataset=False,
    ):
        runtime = _shared_runtime(data_graph)
        if runtime is not None:
            if data_graph_format is not None:
                raise ValueError("data_graph_format is unavailable for a native source")
            shared = runtime._native
            _check_shared_engine(shared)
            if self._shared_program is None:
                self._shared_program = shared.SharedShapes.from_compiled(
                    self._native, _comparison_policy=_native._VALUE_COMPARISON_POLICY
                )
            execute = getattr(data_graph, "_expand_shared_shapes", None)
            if not callable(execute):
                raise RuntimeError("Native source does not implement borrowed SHACL rules")
            namespaces = (
                dict(data_graph.namespaces())
                if isinstance(data_graph, Graph)
                else dict(self._shape_namespaces)
            )
            settings = {
                "iterate_rules": iterate_rules,
                "max_rule_iterations": max_rule_iterations,
                "max_validation_depth": 15
                if max_validation_depth is None
                else max_validation_depth,
                "focus_nodes": _expand_names(namespaces, focus_nodes),
                "use_shapes": _expand_names(dict(self._shape_namespaces), use_shapes),
            }
            try:
                with execute(self._shared_program, json.dumps(settings), inplace) as result:
                    expanded, recursion_warnings = result
                    _check_rule_output(runtime, data_graph, expanded, inplace)
                    _emit_recursion_warnings(recursion_warnings)
            except shared.SharedValidationFailure as failure:
                raise ValidationFailure(str(failure)) from failure
            return expanded
        if inplace and not (
            isinstance(data_graph, (Graph, Input)) or is_oxigraph_store(data_graph)
        ):
            raise TypeError("inplace=True requires an RDFLib Graph or pyoxigraph Store")
        data = _input(data_graph, data_graph_format, direct=True)
        expanded, recursion_warnings = self._native.expand(
            data.source,
            data.format,
            data.base,
            iterate_rules,
            max_rule_iterations,
            15 if max_validation_depth is None else max_validation_depth,
            _expand_names(data.namespaces or dict(self._shape_namespaces), focus_nodes),
            _expand_names(dict(self._shape_namespaces), use_shapes),
            inplace and isinstance(data_graph, Graph),
            _comparison_policy=_native._VALUE_COMPARISON_POLICY,
        )
        _emit_recursion_warnings(recursion_warnings)
        if inplace and isinstance(data_graph, Graph):
            commit_serialized(data_graph, expanded, data.blank_nodes)
            return data_graph
        result = _graph(
            expanded,
            data.blank_nodes,
            multigraph=_return_dataset,
            _bind_namespaces="core" if _return_dataset else "rdflib",
            preserve_ids=True,
            identifier=getattr(data_graph, "identifier", None),
        )
        for prefix, namespace in data.namespaces.items():
            result.bind(prefix, namespace)
        if inplace:
            commit_serialized(data_graph, expanded, data.blank_nodes, before=data)
        return result


def compile_shapes(shacl_graph, *, shacl_graph_format=None, advanced=False):
    return CompiledShapes(shacl_graph, shacl_graph_format=shacl_graph_format, advanced=advanced)


@_failure_result
def validate(
    data_graph,
    *args,
    shacl_graph=None,
    data_graph_format=None,
    shacl_graph_format=None,
    advanced=False,
    inplace=False,
    iterate_rules=False,
    max_rule_iterations=100,
    max_validation_depth=15,
    inference=None,
    ont_graph=None,
    js=False,
    debug=False,
    allow_infos=False,
    allow_warnings=False,
    abort_on_first=False,
    focus_nodes=None,
    use_shapes=None,
    multi_data_graphs_mode=None,
    do_owl_imports=False,
    ont_graph_format=None,
    serialize_report_graph=False,
    sparql_mode=False,
    **kwargs,
):
    report_normalize = kwargs.pop("_normalize_report_literals", True)
    check_dash = kwargs.pop("check_dash_result", False)
    meta_shacl = kwargs.pop("meta_shacl", kwargs.pop("metashacl", False))
    abort_on_first = kwargs.pop("abort_on_error", abort_on_first)
    _options(js, kwargs)
    if debug:
        logging.getLogger("pyshacl-turbo").debug("Validating with the native Rust engine")
    if sparql_mode:
        if inference not in (None, "none") or ont_graph is not None or inplace:
            raise RuntimeError(
                "SPARQL Remote Graph Mode does not support inference, ontology inoculation or inplace"
            )
        if isinstance(data_graph, str) and data_graph.startswith(("http:", "https:")):
            raise NotImplementedError("Remote SPARQL endpoint input")
    if _is_multi_data_graph_input(data_graph):
        if not data_graph:
            raise RuntimeError("No data graphs were provided for validation.")
        if multi_data_graphs_mode == "validate_each":
            return validate_each(
                data_graph,
                *args,
                shacl_graph=shacl_graph,
                advanced=advanced,
                data_graph_format=data_graph_format,
                shacl_graph_format=shacl_graph_format,
                inference=inference,
                ont_graph=ont_graph,
                inplace=inplace,
                allow_infos=allow_infos,
                allow_warnings=allow_warnings,
                abort_on_first=abort_on_first,
                focus_nodes=focus_nodes,
                use_shapes=use_shapes,
                do_owl_imports=do_owl_imports,
                ont_graph_format=ont_graph_format,
                serialize_report_graph=serialize_report_graph,
                iterate_rules=iterate_rules,
                max_rule_iterations=max_rule_iterations,
                max_validation_depth=max_validation_depth,
                debug=debug,
                sparql_mode=sparql_mode,
            )
        if multi_data_graphs_mode not in (None, "combine"):
            raise RuntimeError(f"Unknown multi_data_graphs_mode: {multi_data_graphs_mode}")
        combined = Graph()
        for source in data_graph:
            source_graph = union(load_from_source(source, rdf_format=data_graph_format))
            combined += source_graph
            for prefix, namespace in source_graph.namespaces():
                combined.bind(prefix, namespace)
        data_graph, data_graph_format = combined, None
    caller_shapes = shacl_graph is not None
    if shacl_graph is None:
        shacl_graph, shacl_graph_format = data_graph, data_graph_format
    if meta_shacl:
        conforms, _, text = meta_validate(shacl_graph, shacl_graph_format=shacl_graph_format)
        if not conforms:
            raise ReportableRuntimeError(
                "SHACL File does not validate against the SHACL Shapes SHACL (MetaSHACL) file.\n"
                + text
            )
    native_validation = _shared_runtime(data_graph) is not None and ont_graph is None
    if native_validation and check_dash and inference not in (None, "none"):
        raise NotImplementedError("Native pre-inference with check_dash_result is not implemented")
    original = data_graph
    if caller_shapes:
        data_graph, shacl_graph = _prepare_public_shapes(
            data_graph,
            shacl_graph,
            data_graph_format,
            shacl_graph_format,
            ont_graph,
            inference,
            do_owl_imports,
        )
    original_snapshot = _input(data_graph) if is_oxigraph_store(data_graph) else None
    inference = inference_mode(inference)
    if not native_validation:
        data_graph = _prepare_data(
            replace(original_snapshot) if original_snapshot is not None else data_graph,
            data_graph_format,
            ont_graph,
            ont_graph_format,
            inference,
            do_owl_imports,
        )
    if check_dash:
        snapshot = _input(data_graph, data_graph_format)
        data_graph = Input(
            snapshot.source,
            snapshot.format,
            snapshot.base,
            snapshot.blank_nodes,
            snapshot.namespaces,
            snapshot.preserve_ids,
        )
    program = _compile_for_data(shacl_graph, data_graph, shacl_graph_format, advanced)
    result = program.validate(
        data_graph,
        data_graph_format=data_graph_format,
        inplace=inplace or check_dash,
        inference=inference if native_validation else None,
        iterate_rules=iterate_rules,
        max_rule_iterations=max_rule_iterations,
        max_validation_depth=max_validation_depth,
        allow_infos=allow_infos,
        allow_warnings=allow_warnings,
        abort_on_first=abort_on_first,
        focus_nodes=focus_nodes,
        use_shapes=use_shapes,
        _normalize_report_literals=report_normalize,
    )
    if inplace and isinstance(original, Graph) and original is not data_graph:
        merge_graph(original, load_from_source(data_graph))
    elif inplace and is_oxigraph_store(original) and original is not data_graph:
        snapshot = _input(data_graph)
        commit_serialized(original, snapshot.source, before=original_snapshot)
    if check_dash:
        from .conformance import check_dash_result

        _, report, text = result
        return check_dash_result(report, program.graph, data_graph), report, text
    if serialize_report_graph:
        conforms, report, text = result
        fmt = serialize_report_graph if isinstance(serialize_report_graph, str) else "turtle"
        result = conforms, report.serialize(format=fmt, encoding="utf-8"), text
    return result


def shacl_rules(
    data_graph,
    *args,
    shacl_graph=None,
    data_graph_format=None,
    shacl_graph_format=None,
    advanced=True,
    inplace=False,
    iterate_rules=False,
    max_rule_iterations=100,
    max_validation_depth=15,
    inference=None,
    ont_graph=None,
    js=False,
    debug=False,
    do_owl_imports=False,
    ont_graph_format=None,
    focus_nodes=None,
    use_shapes=None,
    serialize_expanded_graph=False,
    serialize_expanded_graph_format=None,
    **kwargs,
):
    _options(js, kwargs)
    caller_shapes = shacl_graph is not None
    if shacl_graph is None:
        shacl_graph, shacl_graph_format = data_graph, data_graph_format
    original = data_graph
    document = _document_source(original)
    if document:
        data_graph = load_from_source(
            original, rdf_format=data_graph_format, multigraph=True, _bind_namespaces="core"
        )
    if caller_shapes:
        data_graph, shacl_graph = _prepare_public_shapes(
            data_graph,
            shacl_graph,
            data_graph_format,
            shacl_graph_format,
            ont_graph,
            inference,
            do_owl_imports,
        )
    original_snapshot = _input(data_graph) if is_oxigraph_store(data_graph) else None
    data_graph = _prepare_data(
        replace(original_snapshot) if original_snapshot is not None else data_graph,
        data_graph_format,
        ont_graph,
        ont_graph_format,
        inference,
        do_owl_imports,
        _bind_namespaces="core" if document else "rdflib",
    )
    result = _compile_for_data(
        shacl_graph, data_graph, shacl_graph_format, advanced, rules=True
    ).shacl_rules(
        data_graph,
        data_graph_format=data_graph_format,
        inplace=inplace,
        iterate_rules=iterate_rules,
        max_rule_iterations=max_rule_iterations,
        max_validation_depth=max_validation_depth,
        focus_nodes=focus_nodes,
        use_shapes=use_shapes,
        **({"_return_dataset": True} if document else {}),
    )
    if inplace and isinstance(original, Graph) and original is not data_graph:
        merge_graph(original, result)
        result = original
    elif inplace and is_oxigraph_store(original) and original is not data_graph:
        commit_serialized(original, _input(data_graph).source, before=original_snapshot)
    if document:
        result = DataGraph.from_rdflib(result)
    if serialize_expanded_graph:
        rdf_format = serialize_expanded_graph_format or "trig"
        if (
            rdf_format in {"json-ld", "nquads"}
            and isinstance(result, Graph)
            and not result.context_aware
        ):
            dataset = Dataset()
            context = dataset.graph(result.identifier)
            context += result
            for prefix, namespace in result.namespaces():
                dataset.bind(prefix, namespace)
            result = dataset
        return result.serialize(format=rdf_format)
    return result


def _emit_recursion_warnings(messages):
    # Emit before committing rule/inference additions. A warnings-as-errors
    # policy must leave the caller's Graph or Store untouched.
    for message in messages:
        warnings.warn(message, ShapeRecursionWarning, stacklevel=3)


def _options(js, kwargs):
    if js:
        raise NotImplementedError("Unsupported SHACL-JS")
    for option in ("meta_shacl", "check_dash_result", "metashacl"):
        if kwargs.pop(option, False):
            raise NotImplementedError(f"Unsupported option: {option}")
    if kwargs:
        raise TypeError(f"Unsupported options: {', '.join(sorted(kwargs))}")


def _expand_names(graph, names):
    result = []
    namespaces = graph if isinstance(graph, dict) else dict(graph.namespaces())
    for name in names or []:
        prefix, sep, local = str(name).partition(":")
        result.append(
            str(namespaces[prefix]) + local if sep and prefix in namespaces else str(name)
        )
    return result


def _prepare_data(
    data, rdf_format, ontology, ontology_format, inference, imports, *, _bind_namespaces="rdflib"
):
    inference = inference_mode(inference)
    if ontology is None and inference in (None, "none"):
        return data
    if _shared_runtime(data) is not None:
        raise NotImplementedError(
            "Prepare native inference on the Dataset or transaction with owlrl-turbo or .infer() before validation; native ontology inoculation is not supported"
        )
    multigraph = not isinstance(data, Graph) or data.context_aware
    if not isinstance(data, (Graph, Input)) and not is_oxigraph_store(data):
        data = load_from_source(data, rdf_format=rdf_format, multigraph=True)
    snapshot = _input(data, rdf_format)
    source, source_format = snapshot.source, snapshot.format
    namespaces = dict(snapshot.namespaces)
    if ontology is not None:
        ont = _input(
            load_from_source(
                ontology,
                rdf_format=ontology_format,
                do_owl_imports=imports,
                _bind_namespaces=_bind_namespaces,
            ),
            flatten=True,
        )
        source = _native.inoculate(source, source_format, ont.source)
        source_format = "nquads"
        for prefix, namespace in ont.namespaces.items():
            namespaces.setdefault(prefix, namespace)
    if inference not in (None, "none"):
        source = _native.infer(
            source, source_format, inference, "urn:pyshacl:inference" if multigraph else None
        )
        source_format = "nquads"
    if is_oxigraph_store(data) or isinstance(data, Input):
        return Input(
            source, source_format, None, snapshot.blank_nodes, namespaces, preserve_ids=True
        )
    result = _graph(
        source, snapshot.blank_nodes, preserve_ids=True, _bind_namespaces=_bind_namespaces
    )
    for prefix, namespace in namespaces.items():
        result.bind(prefix, namespace)
    return result


def _is_multi_data_graph_input(value):
    return not isinstance(value, (str, bytes, Graph)) and isinstance(
        value, (Sequence, set, frozenset)
    )


def validate_each(data_graphs, *args, **kwargs):
    if not _is_multi_data_graph_input(data_graphs):
        raise ReportableRuntimeError("validate_each expects a sequence of data graphs to validate.")
    data_graphs = list(data_graphs)
    if not data_graphs:
        raise ReportableRuntimeError("No data graphs were provided for validate_each.")
    return {index: validate(data, *args, **kwargs) for index, data in enumerate(data_graphs)}


def meta_validate(shacl_graph, inference="rdfs", **kwargs):
    kwargs.pop("meta_shacl", None)
    kwargs.pop("metashacl", None)
    source_format = kwargs.pop("shacl_graph_format", None)
    source = load_from_source(shacl_graph, rdf_format=source_format)
    return validate(
        source,
        shacl_graph=Path(__file__).parent / "assets/shacl-shacl.ttl",
        inference=inference,
        **kwargs,
    )


from .conformance import evaluate_query_testcase, extract_query_and_expected_result
