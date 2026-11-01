"""RDF I/O only. Parsing and lexical term preservation use the native parser."""

import sys
from dataclasses import dataclass, field
from decimal import localcontext
from io import StringIO
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, url2pathname, urlopen

from rdflib import BNode, Dataset, Graph, Literal, URIRef
from rdflib.namespace import OWL, NamespaceManager
from rdflib.plugins.parsers.nquads import NQuadsParser
from rdflib.plugins.parsers.ntriples import (
    ParseError,
    W3CNTriplesParser,
    r_literal,
    r_tail,
    r_wspace,
    unquote,
    uriquote,
)
from rdflib.util import guess_format

from . import _native
from .term_input import _TermBatch


class _Parser(NQuadsParser):
    def literal(self):
        if not self.peek('"'):
            return False
        lexical, language, datatype = self.eat(r_literal).groups()
        datatype = URIRef(uriquote(unquote(datatype))) if datatype else None
        return Literal(unquote(lexical), language or None, datatype, normalize=False)

    def parseline(self, bnode_context=None):
        self.eat(r_wspace)
        if not self.line or self.line.startswith("#"):
            return
        subject = self.subject(bnode_context)
        self.eat(r_wspace)
        predicate = self.predicate()
        self.eat(r_wspace)
        value = self.object(bnode_context)
        self.eat(r_wspace)
        context = self.uriref() or self.nodeid(bnode_context)
        self.eat(r_tail)
        if self.line:
            raise ParseError("Trailing content in native RDF output")
        graph = self.sink.graph(context) if context else self.sink.default_graph
        graph.add((subject, predicate, value))


class _NativeBlankNodes(dict):
    def get(self, key, default=None):
        return self.setdefault(key, BNode(key))


def _decoded_dataset(bind_namespaces):
    result = Dataset(default_union=True)
    if bind_namespaces != "rdflib":
        result.namespace_manager = NamespaceManager(result, bind_namespaces)
        result.default_graph.namespace_manager = result.namespace_manager
    return result


def decode(
    source,
    blank_nodes=None,
    multigraph=False,
    preserve_ids=False,
    identifier=None,
    *,
    report=False,
    normalize=None,
    _report_conforms=None,
    _bind_namespaces="rdflib",
):
    if report:
        from .report_decode import decode_report

        return decode_report(
            source,
            blank_nodes,
            multigraph,
            preserve_ids,
            identifier,
            normalize,
            conforms=_report_conforms,
        )
    if _report_conforms is not None:
        raise ValueError("Native conformance context requires report decoding")
    if not isinstance(source, str):
        return _decode_terms(
            source,
            blank_nodes,
            multigraph,
            preserve_ids,
            identifier,
            _bind_namespaces=_bind_namespaces,
        )
    dataset = _decoded_dataset(_bind_namespaces)
    parser = _Parser()
    parser.sink = dataset
    nodes = blank_nodes if blank_nodes is not None else {}
    if preserve_ids:
        nodes = _NativeBlankNodes(nodes)
    W3CNTriplesParser.parse(parser, StringIO(source), bnode_context=nodes)
    named = any(g.identifier != dataset.default_graph.identifier for g in dataset.graphs())
    if multigraph or named:
        return dataset
    graph = Graph(identifier=identifier, bind_namespaces=_bind_namespaces)
    graph += dataset.default_graph
    return graph


def _decode_terms(
    source,
    blank_nodes,
    multigraph,
    preserve_ids,
    identifier,
    *,
    copied_subjects=None,
    generated_boolean=None,
    boolean_values=None,
    selected_values=None,
    normalize=None,
    _bind_namespaces="rdflib",
):
    records, quads = source
    nodes = blank_nodes if blank_nodes is not None else {}
    if preserve_ids:
        nodes = _NativeBlankNodes(nodes)
    terms = []
    for kind, value, datatype, language in records:
        if kind == 0:
            term = URIRef(value)
        elif kind == 1:
            term = nodes.get(value)
            if term is None:
                term = nodes.setdefault(value, BNode())
        elif kind == 2:
            term = (
                Literal(value, language, URIRef(datatype) if datatype else None, normalize=False)
                if copied_subjects is None
                else None
            )
        else:
            raise ValueError("Invalid native RDF term record")
        terms.append(term)
    if copied_subjects is not None:
        # Direct report terms restore existing values; conversion must not signal again.
        # One report-local context and the existing terms vector avoid per-term contexts.
        with localcontext():
            for quad_index, quad in enumerate(quads):
                subject, _, obj, _ = quad
                if boolean_values is not None and quad_index in boolean_values:
                    continue
                if generated_boolean is not None and tuple(quad) == generated_boolean[0]:
                    continue
                if subject not in copied_subjects and records[obj][0] == 2 and terms[obj] is None:
                    _, lexical, datatype, language = records[obj]
                    terms[obj] = Literal(
                        lexical,
                        language,
                        URIRef(datatype) if datatype else None,
                        normalize=False,
                    )
    named = multigraph or any(g is not None for _, _, _, g in quads)
    result = (
        _decoded_dataset(_bind_namespaces)
        if named
        else Graph(identifier=identifier, bind_namespaces=_bind_namespaces)
    )
    for quad_index, quad in enumerate(quads):
        s, p, o, g = quad
        destination = (
            (result.default_graph if g is None else result.graph(terms[g])) if named else result
        )
        value = terms[o]
        if generated_boolean is not None and tuple(quad) == generated_boolean[0]:
            value = Literal(generated_boolean[1], normalize=False)
        elif selected_values is not None and quad_index in selected_values:
            value = selected_values[quad_index]
        elif boolean_values is not None and quad_index in boolean_values:
            from rdflib_turbo._literal import restore_boolean

            value = restore_boolean(records[o][1], *boolean_values[quad_index])
        elif copied_subjects is not None and records[o][0] == 2:
            copied = s in copied_subjects
            if copied:
                _, lexical, datatype, language = records[o]
                value = Literal(
                    lexical,
                    language,
                    URIRef(datatype) if datatype else None,
                    normalize=normalize,
                )
        destination.add((terms[s], terms[p], value))
    return result


def _term_input(
    source, *, flatten=False, observe_booleans=False, dataset_factory=None, borrow=False, view=None
):
    nodes = {}
    if observe_booleans:
        native = _native.BooleanInput(
            source,
            nodes,
            flatten,
            _terms=(URIRef, BNode, Literal),
            _dataset=dataset_factory,
            _view=view if borrow else None,
        )
        return Input(native, "terms", None, nodes, dict(source.namespaces()))
    batch = _TermBatch(nodes)
    if source.context_aware:
        default = source.default_graph.identifier
        for s, p, o, g in source.quads():
            batch.append(s, p, o, None if flatten or g == default else g)
    else:
        for s, p, o in source:
            batch.append(s, p, o)
    return Input((batch.records, batch.quads), "terms", None, nodes, dict(source.namespaces()))


def shape_batches(source, nodes):
    """Transfer exact shapes quads with bounded input ownership."""
    batch = _TermBatch(nodes, preserve_empty_datatypes=True)
    if source.context_aware:
        default = (
            source.default_graph.identifier
            if isinstance(source, Dataset)
            else source.default_context.identifier
        )
        rows = (
            (s, p, o, getattr(g, "identifier", g))
            for s, p, o, g in source.quads((None, None, None, None))
        )
    else:
        default = None
        rows = ((s, p, o, None) for s, p, o in source)
    limit = _native.SHAPES_BATCH_SIZE
    for s, p, o, graph in rows:
        batch.append(s, p, o, None if graph == default else graph, retain_graph_owner=False)
        if len(batch.quads) == limit:
            yield batch.records, batch.quads
            batch = _TermBatch(nodes, preserve_empty_datatypes=True)
    if batch.quads:
        yield batch.records, batch.quads


def shape_graphs(source, nodes):
    """Retain declared named contexts, including empty contexts, as typed names."""
    if not source.context_aware:
        return
    if isinstance(source, Dataset):
        default = source.default_graph.identifier
        contexts = source.graphs()
    else:
        default = source.default_context.identifier
        contexts = source.contexts()
    for context in contexts:
        if context.identifier != default:
            batch = _TermBatch(nodes)
            batch.intern(context.identifier, retain_blank_owner=False)
            yield batch.records[0]


def union(source):
    graph = Graph()
    for prefix, namespace in source.namespaces():
        graph.bind(prefix, namespace)
    if source.context_aware:
        for s, p, o, _ in source.quads((None, None, None, None)):
            graph.add((s, p, o))
    else:
        graph += source
    return graph


def _document(source, rdf_format):
    base = None
    if hasattr(source, "read"):
        body = source.read()
        if getattr(source, "name", None):
            base = Path(source.name).resolve().as_uri()
    elif isinstance(source, Path):
        source = source.resolve(strict=True)
        base, body = source.as_uri(), source.read_bytes()
        rdf_format = rdf_format or guess_format(source.name)
    elif isinstance(source, bytes):
        body = source
    elif isinstance(source, str):
        stripped = source.lstrip()
        if stripped.startswith(("http://", "https://", "file:")) and "\n" not in source:
            if stripped.startswith("file:"):
                return _document(Path(url2pathname(urlparse(source).path)), rdf_format)
            request = Request(
                source,
                headers={
                    "Accept": "text/turtle,application/rdf+xml,application/ld+json,application/n-quads"
                },
            )
            with urlopen(request, timeout=30) as response:
                base, body = response.geturl(), response.read()
                media = response.headers.get_content_type()
                rdf_format = (
                    rdf_format
                    or {
                        "text/turtle": "turtle",
                        "application/rdf+xml": "xml",
                        "application/ld+json": "json-ld",
                        "application/n-quads": "nquads",
                        "application/trig": "trig",
                        "application/n-triples": "nt",
                    }.get(media)
                    or guess_format(urlparse(base).path)
                )
        elif "\n" in source or stripped.startswith(("@", "PREFIX", "BASE", "<", "{", "[", "#")):
            body = source
        else:
            return _document(Path(source), rdf_format)
    else:
        raise TypeError("Expected an RDF graph, RDF text, bytes, file, path or URL")
    text = body.decode("utf-8-sig") if isinstance(body, bytes) else body
    if rdf_format is None:
        stripped = text.lstrip()
        if stripped.startswith(("{", "[")):
            rdf_format = "json-ld"
        elif stripped.startswith("<?xml") or "<rdf:RDF" in stripped[:500]:
            rdf_format = "xml"
        else:
            rdf_format = "turtle"
    return text, rdf_format, base or Path.cwd().as_uri() + "/"


def load_from_source(
    source,
    *,
    g=None,
    rdf_format=None,
    multigraph=False,
    do_owl_imports=False,
    logger=None,
    _bind_namespaces="rdflib",
    **kwargs,
):
    if kwargs:
        raise TypeError(f"Unsupported loader options: {', '.join(sorted(kwargs))}")
    if isinstance(source, Graph):
        result = source
    elif isinstance(source, Input):
        text = source.source
        if source.format == "oxigraph-nquads":
            text, _ = _native.parse_rdf(text, source.format, source.base)
        result = decode(
            text,
            source.blank_nodes,
            multigraph=multigraph,
            preserve_ids=source.preserve_ids,
            _bind_namespaces=_bind_namespaces,
        )
    elif is_oxigraph_store(source):
        snapshot = input_graph(source)
        result = load_from_source(
            snapshot, multigraph=multigraph, _bind_namespaces=_bind_namespaces
        )
    else:
        text, rdf_format, base = _document(source, rdf_format)
        nquads, prefixes = _native.parse_rdf(text, rdf_format, base)
        result = decode(nquads, multigraph=multigraph, _bind_namespaces=_bind_namespaces)
        for prefix, namespace in prefixes:
            result.bind(prefix, namespace)
    if do_owl_imports:
        result = union(result)
        visited = set()
        pending = list(result.objects(None, OWL.imports))
        while pending:
            url = pending.pop()
            if url in visited:
                continue
            if not isinstance(url, URIRef):
                raise TypeError(f"owl:imports must name an IRI: {url}")
            visited.add(url)
            imported = load_from_source(str(url))
            result += union(imported)
            pending.extend(imported.objects(None, OWL.imports))
    if g is not None:
        for triple in union(result):
            g.add(triple)
        return g
    return result


@dataclass
class Input:
    source: str | tuple
    format: str
    base: str | None
    blank_nodes: dict
    namespaces: dict = field(default_factory=dict)
    preserve_ids: bool = False


def is_oxigraph_store(source):
    module = sys.modules.get("pyoxigraph")
    return module is not None and isinstance(source, module.Store)


def commit_serialized(target, source, nodes=None, *, before=None):
    if is_oxigraph_store(target):
        import pyoxigraph

        if before is None:
            raise ValueError("Store commits require the original input snapshot")
        source = _native.additions(before.source, before.format, source)
        # extend is atomic, and parse preserves labels shared with existing data.
        target.extend(
            pyoxigraph.parse(source, format=pyoxigraph.RdfFormat.N_QUADS, rename_blank_nodes=False)
        )
    elif isinstance(target, Input):
        target.source = source
        target.format = "nquads" if isinstance(source, str) else "terms"
    else:
        if before is not None:
            source = _native.additions(before.source, before.format, source)
        merge_graph(target, decode(source, nodes, preserve_ids=True))


def input_graph(
    source,
    rdf_format=None,
    *,
    flatten=False,
    direct=False,
    observe_booleans=False,
    _dataset_factory=None,
    _borrow=False,
):
    from .graph_abstraction import DataGraph, _reject_native_store_graph

    view = source if isinstance(source, DataGraph) else None
    if view is not None:
        source = source.impl
    _reject_native_store_graph(source)
    if isinstance(source, Input):
        if flatten:
            return input_graph(load_from_source(source), flatten=True)
        return source
    if is_oxigraph_store(source) and not flatten:
        import pyoxigraph

        return Input(
            source.dump(format=pyoxigraph.RdfFormat.N_QUADS).decode("utf-8"),
            "oxigraph-nquads",
            None,
            {},
            preserve_ids=True,
        )
    if not isinstance(source, Graph):
        source = load_from_source(source, rdf_format=rdf_format)
    if direct:
        borrow = _borrow and not source.context_aware
        if borrow and view is None:
            view = DataGraph.from_rdflib_graph(source)
        return _term_input(
            source,
            flatten=flatten,
            observe_booleans=observe_booleans,
            dataset_factory=_dataset_factory,
            borrow=borrow,
            view=view if borrow else None,
        )
    graph = union(source) if source.context_aware else source
    nodes = {str(n): n for n in graph.all_nodes() if isinstance(n, BNode)}
    if source.context_aware and not flatten:
        lines = []
        for context in source.graphs():
            suffix = (
                ""
                if context.identifier == source.default_graph.identifier
                else " " + context.identifier.n3()
            )
            if isinstance(context.identifier, BNode):
                nodes[str(context.identifier)] = context.identifier
            # RDFLib's NT serializer emits one triple per line and no lines for
            # an empty context; escaped literal newlines stay inside that line.
            for line in context.serialize(format="nt").splitlines():
                lines.append(line.rstrip().removesuffix(".").rstrip() + suffix + " .")
        return Input("\n".join(lines), "nquads", None, nodes, dict(source.namespaces()))
    return Input(graph.serialize(format="nt"), "nt", None, nodes, dict(source.namespaces()))


def copy_graph(source):
    from .graph_abstraction import _reject_native_store_graph

    _reject_native_store_graph(source)
    if not source.context_aware:
        return union(source)
    result = Dataset(default_union=True)
    for context in source.graphs():
        target = (
            result.default_graph
            if context.identifier == source.default_graph.identifier
            else result.graph(context.identifier)
        )
        target += context
    for prefix, namespace in source.namespaces():
        result.bind(prefix, namespace)
    return result


def merge_graph(target, source):
    from .graph_abstraction import DataGraph, _reject_native_store_graph

    if isinstance(target, DataGraph):
        target = target.impl
    if isinstance(source, DataGraph):
        source = source.impl
    _reject_native_store_graph(target)
    _reject_native_store_graph(source)
    if source.context_aware and target.context_aware:
        for context in source.graphs():
            destination = (
                target.default_graph
                if context.identifier == source.default_graph.identifier
                else target.graph(context.identifier)
            )
            destination += context
    elif target.context_aware:
        target.default_graph += source
    else:
        target += union(source) if source.context_aware else source
    return target
