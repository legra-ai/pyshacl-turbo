"""``pyshacl.graph_abstraction``: data-graph wrappers and the Oxigraph availability flag."""

from importlib.util import find_spec

from pyshacl_turbo.graph_abstraction import DataGraph, RdfLibDataGraph

has_oxigraph = find_spec("pyoxigraph") is not None
"""True when the optional pyoxigraph Store support is installed, as in pySHACL."""

__all__ = ["DataGraph", "RdfLibDataGraph", "has_oxigraph"]
