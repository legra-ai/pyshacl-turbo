"""Explicit immutable data snapshots for repeated shape targeting."""

from rdflib import BNode, Literal, URIRef

from . import _native
from .rdf import decode, input_graph


class TargetData:
    """One data snapshot, reusable across shapes and focus-node calls.

    Changes to the original graph are visible only after preparing a new snapshot.
    Cached target sets belong to this snapshot and the immutable compiled shapes.
    """

    def __init__(self, data_graph):
        data = input_graph(data_graph, direct=True)
        self._native = _native.TargetData(data.source, data.format, data.base)
        self._blank_nodes = data.blank_nodes
        self._results = {}
        self._targeting_indexes = {}

    def _focus_nodes(self, compiled, node, advanced):
        key = (compiled, node, advanced)
        if key not in self._results:
            output = compiled._native.focus_nodes(node.n3(), self._native, advanced)
            result = decode(output, compiled._blank_nodes | self._blank_nodes, preserve_ids=True)
            self._results[key] = frozenset(result.objects())
        return set(self._results[key])

    def _targeting(self, compiled, node, skip):
        if not isinstance(node, (URIRef, BNode, Literal)):
            raise TypeError("node must be an RDFLib IRI, blank node, or literal")
        if isinstance(skip, (str, BNode, Literal)):
            raise TypeError("skip must be an iterable of shape IRIs or blank nodes")
        skip = frozenset(skip)
        if any(not isinstance(shape, (URIRef, BNode)) for shape in skip):
            raise TypeError("skip must contain only shape IRIs or blank nodes")
        key = (compiled, skip)
        if key not in self._targeting_indexes:
            output = compiled._native.targeting_index(
                self._native, sorted(shape.n3() for shape in skip)
            )
            result = decode(output, compiled._blank_nodes | self._blank_nodes, preserve_ids=True)
            index = {}
            for shape, _, focus in result:
                index.setdefault(focus, set()).add(shape)
            self._targeting_indexes[key] = {
                focus: tuple(sorted(shapes, key=lambda shape: shape.n3()))
                for focus, shapes in index.items()
            }
        return list(self._targeting_indexes[key].get(node, ()))


def prepare_target_data(data_graph):
    """Snapshot data once for repeated ``Shape.focus_nodes`` calls.

    Preparing an existing TargetData returns it unchanged. Prepare the original
    graph again when its mutations should become visible.
    """
    return data_graph if isinstance(data_graph, TargetData) else TargetData(data_graph)
