"""Decode report occurrences using reference description-copy literal policy."""

from io import StringIO

from rdflib import BNode, URIRef
from rdflib.namespace import RDF, SH, XSD
from rdflib.plugins.parsers.ntriples import W3CNTriplesParser, r_literal, unquote, uriquote

from .rdf import _decode_terms, _NativeBlankNodes, _Parser


class _QuadSink:
    def __init__(self, owner, graph):
        self.owner, self.graph = owner, graph

    def add(self, triple):
        self.owner.quads.append(
            (
                *[self.owner.intern(node) for node in triple],
                None if self.graph is None else self.owner.intern(self.graph),
            )
        )


class _ReportSink:
    def __init__(self):
        self.records, self.quads, self.indices = [], [], {}
        self.default_graph = _QuadSink(self, None)

    def graph(self, graph):
        return _QuadSink(self, graph)

    def intern(self, node):
        if isinstance(node, URIRef):
            record = (0, str(node), None, None)
        elif isinstance(node, BNode):
            record = (1, str(node), None, None)
        else:
            record = node
        if record not in self.indices:
            self.indices[record] = len(self.records)
            self.records.append(record)
        return self.indices[record]


class _ReportParser(_Parser):
    def literal(self):
        if not self.peek('"'):
            return False
        lexical, language, datatype = self.eat(r_literal).groups()
        datatype = uriquote(unquote(datatype)) if datatype else None
        # Retain lexical records until blank-description reachability is known.
        return 2, unquote(lexical), datatype, language or None


def _description_subjects(records, quads):
    def iri(index, expected):
        return records[index][0] == 0 and records[index][1] == str(expected)

    results = {
        subject
        for subject, predicate, value, _ in quads
        if iri(predicate, RDF.type) and iri(value, SH.ValidationResult)
    }
    edges, pending = {}, []
    roots = {
        str(node)
        for node in (SH.sourceShape, SH.focusNode, SH.value, SH.resultPath, SH.sourceConstraint)
    }
    for subject, predicate, value, _ in quads:
        if records[value][0] != 1:
            continue
        edges.setdefault(subject, []).append(value)
        if subject in results and records[predicate][1] in roots:
            pending.append(value)
    seen = set()
    while pending:
        node = pending.pop()
        if node not in seen:
            seen.add(node)
            pending.extend(edges.get(node, ()))
    return seen


def _generated_boolean(records, quads, copied_subjects, conforms):
    if conforms is None:
        return None
    if type(conforms) is not bool:
        raise TypeError("Native report conformance must be a boolean")

    def iri(index, value):
        return records[index][0] == 0 and records[index][1] == str(value)

    root = None
    for subject, predicate, value, context in quads:
        if (
            subject not in copied_subjects
            and iri(predicate, RDF.type)
            and iri(value, SH.ValidationReport)
        ):
            if root is not None:
                raise ValueError("Native report has multiple generated roots")
            root = subject, context
    if root is None:
        raise ValueError("Native report is missing its generated root")
    header = None
    expected = (2, "true" if conforms else "false", str(XSD.boolean), None)
    for quad in quads:
        subject, predicate, value, context = quad
        if subject == root[0] and context == root[1] and iri(predicate, SH.conforms):
            if header is not None or tuple(records[value]) != expected:
                raise ValueError("Native report has an invalid conformance header")
            header = tuple(quad)
    if header is None:
        raise ValueError("Native report is missing its conformance header")
    return header, conforms


def decode_report(
    source, blank_nodes, multigraph, preserve_ids, identifier, normalize, *, conforms=None
):
    if isinstance(source, str):
        sink, parser = _ReportSink(), _ReportParser()
        parser.sink = sink
        nodes = blank_nodes if blank_nodes is not None else {}
        if preserve_ids:
            nodes = _NativeBlankNodes(nodes)
        W3CNTriplesParser.parse(parser, StringIO(source), bnode_context=nodes)
        source = sink.records, sink.quads
    records, quads = source
    copied_subjects = _description_subjects(records, quads)
    generated_boolean = _generated_boolean(records, quads, copied_subjects, conforms)
    return _decode_terms(
        source,
        blank_nodes,
        multigraph,
        preserve_ids,
        identifier,
        copied_subjects=copied_subjects,
        generated_boolean=generated_boolean,
        normalize=normalize,
        _bind_namespaces="core",
    )
