"""Format caller-supplied report results without executing SHACL constraints."""

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import RDF, SH


class ReportBuilder:
    def __init__(self, shapes):
        self.graph = Graph(bind_namespaces="core")
        for prefix, namespace in shapes.graph.namespaces():
            self.graph.bind(prefix, namespace)
        self.nodes = {}

    @classmethod
    def build(cls, shapes, conforms, results):
        if not conforms and not results:
            raise RuntimeError("A Non-Conformant Validation Report must have at least one result.")
        builder = cls(shapes)
        root = BNode()
        builder.graph.add((root, RDF.type, SH.ValidationReport))
        builder.graph.add((root, SH.conforms, Literal(conforms)))
        text = f"Validation Report\nConforms: {conforms}\n"
        if results:
            text += f"Results ({len(results)}):\n"
            text += "".join(
                description for description, _, _ in sorted(results, key=lambda r: r[0])
            )
        for _, node, triples in results:
            builder.graph.add((root, SH.result, node))
            for subject, predicate, value in triples:
                if isinstance(value, tuple):
                    value = builder.source_node(*value)
                builder.graph.add((subject, predicate, value))
        return builder.graph, text

    def source_node(self, source, node):
        if isinstance(node, Literal):
            return node
        key = source, str(node)
        if key not in self.nodes:
            self.nodes[key] = (
                self.blank_node(source, node, 0, keepid=True)
                if isinstance(node, BNode)
                else URIRef(str(node))
            )
        return self.nodes[key]

    def blank_node(self, source, node, depth, *, keepid=False):
        result = BNode(str(node)) if keepid else BNode()
        # bounded: the public report view follows the reference's ten-level limit.
        if depth >= 10:
            return result
        predicates = set(source.predicates(node))
        if RDF.first in predicates:
            collection = Collection(self.graph, result)
            for value in source.items(node):
                collection.append(self.clone_node(source, value, depth + 1))
            return result
        for predicate in predicates:
            copied_predicate = self.clone_node(source, predicate, depth + 1)
            for value in source.objects(node, predicate):
                self.graph.add(
                    (result, copied_predicate, self.clone_node(source, value, depth + 1))
                )
        return result

    def clone_node(self, source, node, depth):
        if isinstance(node, BNode):
            return self.blank_node(source, node, depth + 1)
        if isinstance(node, Literal):
            return Literal(str(node), lang=node.language, datatype=node.datatype)
        if isinstance(node, URIRef):
            return URIRef(str(node))
        raise ValueError(f"Cannot clone node of type {type(node)}")
