"""RDF I/O only. Parsing and lexical term preservation use the native parser."""

import sys
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from urllib.parse import unquote as url_unquote
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from rdflib import BNode, Dataset, Graph, Literal, URIRef
from rdflib.namespace import OWL
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


def decode(source, blank_nodes=None, multigraph=False, preserve_ids=False):
    dataset = Dataset(default_union=True)
    parser = _Parser()
    parser.sink = dataset
    nodes = blank_nodes if blank_nodes is not None else {}
    if preserve_ids:
        nodes = _NativeBlankNodes(nodes)
    W3CNTriplesParser.parse(parser, StringIO(source), bnode_context=nodes)
    named = any(g.identifier != dataset.default_graph.identifier for g in dataset.graphs())
    if multigraph or named:
        return dataset
    graph = Graph()
    graph += dataset.default_graph
    return graph


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
                return _document(Path(url_unquote(urlparse(source).path)), rdf_format)
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
        )
    elif is_oxigraph_store(source):
        snapshot = input_graph(source)
        result = load_from_source(snapshot, multigraph=multigraph)
    else:
        text, rdf_format, base = _document(source, rdf_format)
        nquads, prefixes = _native.parse_rdf(text, rdf_format, base)
        result = decode(nquads, multigraph=multigraph)
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
    source: str
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
        target.source, target.format = source, "nquads"
    else:
        merge_graph(target, decode(source, nodes, preserve_ids=True))


def input_graph(source, rdf_format=None, *, flatten=False):
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
            for line in context.serialize(format="nt").splitlines():
                if line.strip():
                    lines.append(line.rstrip().removesuffix(".").rstrip() + suffix + " .")
        return Input("\n".join(lines), "nquads", None, nodes, dict(source.namespaces()))
    return Input(graph.serialize(format="nt"), "nt", None, nodes, dict(source.namespaces()))


def copy_graph(source):
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
