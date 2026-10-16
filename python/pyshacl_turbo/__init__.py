"""pySHACL compatibility layer. All SHACL execution happens in Rust."""

import logging
import warnings
from collections.abc import Iterable, Sequence
from dataclasses import replace
from functools import lru_cache, wraps
from importlib.metadata import version
from pathlib import Path

from rdflib import BNode, Dataset, Graph, Literal, URIRef

from . import _native
from .errors import ReportableRuntimeError, ShapeRecursionWarning, ValidationWarning
from .rdf import (
    Input,
    commit_serialized,
    is_oxigraph_store,
    load_from_source,
    merge_graph,
    union,
)
from .rdf import decode as _graph
from .rdf import input_graph as _input
from .shape import Shape
from .shapes_graph import ShapesGraph
from .target_data import TargetData, prepare_target_data

ValidationFailure = _native.ValidationFailure
__version__ = version("pyshacl-turbo")


def _failure_result(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except ValidationFailure as failure:
            failure.message = str(failure)
            return False, failure, f"Validation Failure - {failure}"
        except NotImplementedError:
            raise
        except RuntimeError as error:
            raise ReportableRuntimeError(str(error)) from error

    return wrapped


__all__ = [
    "CompiledShapes",
    "ReportableRuntimeError",
    "Shape",
    "ShapeRecursionWarning",
    "ShapesGraph",
    "TargetData",
    "ValidationFailure",
    "ValidationWarning",
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
def _compile_native(source, rdf_format, base, advanced, numeric_booleans, namespaces):
    return _native.CompiledShapes(
        source, rdf_format, base, advanced, numeric_booleans, list(namespaces)
    )


class CompiledShapes:
    """Reusable immutable shapes; each call gets its own Rust data store."""

    def __init__(self, shacl_graph, *, shacl_graph_format=None, advanced=False):
        self.graph = load_from_source(shacl_graph, rdf_format=shacl_graph_format)
        shapes = _input(self.graph, flatten=True)
        self._blank_nodes = shapes.blank_nodes
        self._native = _compile_native(
            "\n".join(sorted(shapes.source.splitlines())),
            shapes.format,
            shapes.base,
            advanced,
            isinstance(shacl_graph, Graph),
            tuple((p, str(ns)) for p, ns in self.graph.namespaces()),
        )

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
        iterate_rules=False,
        max_rule_iterations=100,
        max_validation_depth=15,
        allow_infos=False,
        allow_warnings=False,
        abort_on_first=False,
        focus_nodes=None,
        use_shapes=None,
    ):
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
            _expand_names(data.namespaces or dict(self.graph.namespaces()), focus_nodes),
            _expand_names(self.graph, use_shapes),
            [(p, str(ns)) for p, ns in data.namespaces.items()],
        )
        _emit_recursion_warnings(recursion_warnings)
        nodes = self._blank_nodes | data.blank_nodes
        report_graph = _graph(report, nodes, preserve_ids=True)
        for prefix, namespace in self.graph.namespaces():
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
    ):
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
            _expand_names(data.namespaces or dict(self.graph.namespaces()), focus_nodes),
            _expand_names(self.graph, use_shapes),
            inplace and isinstance(data_graph, Graph),
        )
        _emit_recursion_warnings(recursion_warnings)
        if inplace and isinstance(data_graph, Graph):
            commit_serialized(data_graph, expanded, data.blank_nodes)
            return data_graph
        result = _graph(
            expanded,
            data.blank_nodes,
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
    if shacl_graph is None:
        shacl_graph, shacl_graph_format = data_graph, data_graph_format
    if meta_shacl:
        conforms, _, text = meta_validate(shacl_graph, shacl_graph_format=shacl_graph_format)
        if not conforms:
            raise ReportableRuntimeError(
                "SHACL File does not validate against the SHACL Shapes SHACL (MetaSHACL) file.\n"
                + text
            )
    if do_owl_imports:
        shacl_graph = load_from_source(
            shacl_graph, rdf_format=shacl_graph_format, do_owl_imports=True
        )
    original = data_graph
    original_snapshot = _input(data_graph) if is_oxigraph_store(data_graph) else None
    data_graph = _prepare_data(
        replace(original_snapshot) if original_snapshot is not None else data_graph,
        data_graph_format,
        ont_graph,
        ont_graph_format,
        inference,
        do_owl_imports,
    )
    program = compile_shapes(shacl_graph, shacl_graph_format=shacl_graph_format, advanced=advanced)
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
    result = program.validate(
        data_graph,
        data_graph_format=data_graph_format,
        inplace=inplace or check_dash,
        iterate_rules=iterate_rules,
        max_rule_iterations=max_rule_iterations,
        max_validation_depth=max_validation_depth,
        allow_infos=allow_infos,
        allow_warnings=allow_warnings,
        abort_on_first=abort_on_first,
        focus_nodes=focus_nodes,
        use_shapes=use_shapes,
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
    if shacl_graph is None:
        shacl_graph, shacl_graph_format = data_graph, data_graph_format
    original = data_graph
    original_snapshot = _input(data_graph) if is_oxigraph_store(data_graph) else None
    data_graph = _prepare_data(
        replace(original_snapshot) if original_snapshot is not None else data_graph,
        data_graph_format,
        ont_graph,
        ont_graph_format,
        inference,
        do_owl_imports,
    )
    if do_owl_imports:
        shacl_graph = load_from_source(
            shacl_graph, rdf_format=shacl_graph_format, do_owl_imports=True
        )
    result = compile_shapes(
        shacl_graph, shacl_graph_format=shacl_graph_format, advanced=advanced
    ).shacl_rules(
        data_graph,
        data_graph_format=data_graph_format,
        inplace=inplace,
        iterate_rules=iterate_rules,
        max_rule_iterations=max_rule_iterations,
        max_validation_depth=max_validation_depth,
        focus_nodes=focus_nodes,
        use_shapes=use_shapes,
    )
    if inplace and isinstance(original, Graph) and original is not data_graph:
        merge_graph(original, result)
        result = original
    elif inplace and is_oxigraph_store(original) and original is not data_graph:
        commit_serialized(original, _input(data_graph).source, before=original_snapshot)
    if serialize_expanded_graph:
        rdf_format = serialize_expanded_graph_format or "trig"
        if rdf_format in {"json-ld", "nquads"} and not result.context_aware:
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


def _prepare_data(data, rdf_format, ontology, ontology_format, inference, imports):
    if ontology is None and inference in (None, "none"):
        return data
    multigraph = not isinstance(data, Graph) or data.context_aware
    if not isinstance(data, (Graph, Input)) and not is_oxigraph_store(data):
        data = load_from_source(data, rdf_format=rdf_format, multigraph=True)
    snapshot = _input(data, rdf_format)
    source, source_format = snapshot.source, snapshot.format
    namespaces = dict(snapshot.namespaces)
    if ontology is not None:
        ont = _input(
            load_from_source(ontology, rdf_format=ontology_format, do_owl_imports=imports),
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
    result = _graph(source, snapshot.blank_nodes, preserve_ids=True)
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
