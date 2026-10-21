"""Shared typed RDF transfer encoding for complete inputs and bounded batches."""

from rdflib import BNode, Literal, URIRef


class _TermBatch:
    def __init__(self, nodes):
        self.records, self.quads, self.indices = [], [], {}
        self.nodes = nodes

    def intern(self, term):
        index = self.indices.get(term)
        if index is not None:
            return index
        if isinstance(term, URIRef):
            record = (0, str(term), None, None)
        elif isinstance(term, BNode):
            self.nodes[str(term)] = term
            record = (1, str(term), None, None)
        elif isinstance(term, Literal):
            record = (
                2,
                str(term),
                str(term.datatype) if term.datatype and not term.language else None,
                term.language,
            )
        else:
            raise TypeError("Expected an RDFLib IRI, blank node or literal")
        index = len(self.records)
        self.indices[term] = index
        self.records.append(record)
        return index

    def append(self, subject, predicate, value, graph=None):
        self.quads.append(
            (
                self.intern(subject),
                self.intern(predicate),
                self.intern(value),
                None if graph is None else self.intern(graph),
            )
        )
