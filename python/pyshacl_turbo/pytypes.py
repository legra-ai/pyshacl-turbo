"""Public execution settings shared by the runner and shape inspection APIs."""

from dataclasses import dataclass

from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.term import IdentifiedNode

GraphLike = Dataset | Graph
RDFNode = IdentifiedNode | Literal


@dataclass
class SHACLExecutor:
    validator: object | None = None
    advanced_mode: bool = False
    abort_on_first: bool = False
    allow_infos: bool = False
    allow_warnings: bool = False
    iterate_rules: bool = False
    debug: bool = False
    sparql_mode: bool = False
    max_validation_depth: int = 15
    focus_nodes: list[URIRef] | None = None
