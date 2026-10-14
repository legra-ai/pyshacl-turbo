"""Explicit immutable data snapshots for repeated shape targeting."""

from . import _native
from .rdf import decode, input_graph


class TargetData:
    """One data snapshot, reusable across shapes and focus-node calls.

    Changes to the original graph are visible only after preparing a new snapshot.
    Cached target sets belong to this snapshot and the immutable compiled shapes.
    """

    def __init__(self, data_graph):
        data = input_graph(data_graph)
        self._native = _native.TargetData(data.source, data.format, data.base)
        self._blank_nodes = data.blank_nodes
        self._results = {}

    def _focus_nodes(self, compiled, node, advanced):
        key = (compiled, node, advanced)
        if key not in self._results:
            output = compiled._native.focus_nodes(node.n3(), self._native, advanced)
            result = decode(output, compiled._blank_nodes | self._blank_nodes, preserve_ids=True)
            self._results[key] = frozenset(result.objects())
        return set(self._results[key])


def prepare_target_data(data_graph):
    """Snapshot data once for repeated ``Shape.focus_nodes`` calls.

    Preparing an existing TargetData returns it unchanged. Prepare the original
    graph again when its mutations should become visible.
    """
    return data_graph if isinstance(data_graph, TargetData) else TargetData(data_graph)
