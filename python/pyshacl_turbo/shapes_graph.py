"""Shape inspection backed by the native structural compiler and target evaluator."""

import logging
from collections.abc import Iterable
from typing import ClassVar

from rdflib import BNode, Dataset, Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS
from rdflib.util import from_n3

from .shape import Shape


class ShapesGraph:
    system_triples: ClassVar[list[tuple[URIRef, URIRef, URIRef]]] = [
        (OWL.Class, RDFS.subClassOf, RDFS.Class),
        (OWL.DatatypeProperty, RDFS.subClassOf, RDF.Property),
    ]

    def __init__(self, graph, debug=False, logger=None):
        if not isinstance(graph, Graph):
            raise TypeError("ShapesGraph requires an RDFLib Graph or Dataset")
        self.graph = graph
        if isinstance(graph, Dataset):
            graph.default_union = True
        self.debug = debug
        self.logger = logger or logging.getLogger(__name__)
        self._compiled = None
        self._node_shape_cache = {}
        self._numeric_booleans = True
        self._add_system_triples()

    def _add_system_triples(self):
        for triple in self.system_triples:
            self.graph.add(triple)

    def _compile(self):
        from . import CompiledShapes

        if self._compiled is None:
            self._compiled = CompiledShapes(self.graph, advanced=True)
        return self._compiled

    @property
    def shapes(self):
        from rdflib.namespace import SH

        if not self._node_shape_cache:
            for term in self._compile()._native.shape_nodes():
                node = from_n3(term)
                path = self.graph.value(node, SH.path)
                self._node_shape_cache[node] = Shape(
                    self, node, p=path is not None, path=path, logger=self.logger
                )
        return self._node_shape_cache.values()

    def lookup_shape_from_node(self, node):
        return self._node_shape_cache[node]

    def targeting(
        self,
        data_graph,
        node: URIRef | BNode | Literal,
        *,
        skip: Iterable[URIRef | BNode] = (),
    ) -> list[URIRef | BNode]:
        """Return active node-shape identifiers targeting node, including AF targets."""
        return self._compile().targeting(data_graph, node, skip=skip)

    def shapes_from_uris(self, shapes_uris):
        if not self._node_shape_cache:
            list(self.shapes)
        return [self._node_shape_cache[node] for node in shapes_uris]

    def objects(self, subject, predicate):
        return self.graph.objects(subject, predicate)

    def subjects(self, predicate, object):
        return self.graph.subjects(predicate, object)

    def predicates(self, subject, object):
        return self.graph.predicates(subject, object)

    def predicate_objects(self, subject):
        return self.graph.predicate_objects(subject)

    def subject_objects(self, predicate):
        return self.graph.subject_objects(predicate)

    def subject_predicates(self, object):
        return self.graph.subject_predicates(object)
