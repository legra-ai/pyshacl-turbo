"""Exact immutable compilation keys without rendering mutable RDFLib graphs."""

from rdflib import BNode, Graph, Literal, URIRef


def snapshot_shapes(source):
    """Read current union contents, retaining only typed lexical values in the key."""
    records, blank_nodes = {}, {}

    def record(term):
        value = records.get(term)
        if value is not None:
            return value
        if isinstance(term, URIRef):
            value = (0, str(term), None, None)
        elif isinstance(term, BNode):
            blank_nodes[str(term)] = term
            value = (1, str(term), None, None)
        elif isinstance(term, Literal):
            value = (
                2,
                str(term),
                str(term.datatype) if term.datatype and not term.language else None,
                term.language,
            )
        else:
            raise TypeError("Expected an RDFLib IRI, blank node or literal")
        records[term] = value
        return value

    triples = (
        ((s, p, o) for s, p, o, _ in source.quads((None, None, None, None)))
        if source.context_aware
        else iter(source)
    )
    return frozenset((record(s), record(p), record(o)) for s, p, o in triples), blank_nodes


def serialize_shapes(snapshot):
    """Render only a cache miss for the native and shared-runtime text inputs."""
    terms = {}

    def term(record):
        value = terms.get(record)
        if value is not None:
            return value
        kind, lexical, datatype, language = record
        if kind == 0:
            value = URIRef(lexical)
        elif kind == 1:
            value = BNode(lexical)
        else:
            value = Literal(
                lexical, language, URIRef(datatype) if datatype else None, normalize=False
            )
        terms[record] = value
        return value

    graph = Graph(bind_namespaces="none")
    for subject, predicate, value in snapshot:
        graph.add((term(subject), term(predicate), term(value)))
    return graph.serialize(format="nt")
