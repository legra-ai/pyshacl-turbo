"""Private shared construction and native preparation for public runner types."""

import logging

from rdflib import Dataset, Graph, URIRef

from .graph_abstraction import DataGraph
from .shapes_graph import ShapesGraph


class Runner:
    @classmethod
    def _load_default_options(cls, options_dict):
        for name, value in cls._defaults.items():
            options_dict.setdefault(name, value)
        if "logger" not in options_dict:
            options_dict["logger"] = logging.getLogger(cls.__module__)
            if options_dict["debug"]:
                options_dict["logger"].setLevel(logging.DEBUG)

    def __init__(self, data_graph, *args, shacl_graph=None, ont_graph=None, options=None, **kwargs):
        options = options or {}
        self._load_default_options(options)
        self.options = options
        self.logger = options["logger"]
        self.debug = options["debug"]
        self.pre_inferenced = kwargs.pop("pre_inferenced", False)
        self.inplace = options["inplace"]
        if not isinstance(data_graph, DataGraph):
            raise RuntimeError("data_graph must be a DataGraph object")  # noqa: TRY004 - reference API
        self.data_graph = data_graph
        self._target_graph = None
        self.ont_graph = ont_graph
        self.data_graph_is_multigraph = data_graph.is_multigraph()
        if isinstance(ont_graph, Dataset):
            ont_graph.default_union = True
        if shacl_graph is None:
            shacl_graph = data_graph.clone(identifier="shacl")
        assert isinstance(shacl_graph, Graph), "shacl_graph must be a rdflib Graph object"
        self.shacl_graph = ShapesGraph(shacl_graph, self.debug, self.logger)

    @property
    def target_graph(self):
        return self._target_graph

    def _prepare_focus_nodes(self, target):
        if self.options.get("focus_nodes"):
            from . import _expand_names

            self.options["focus_nodes"] = [
                URIRef(node) for node in _expand_names(target.impl, self.options["focus_nodes"])
            ]

    def mix_in_ontology(self):
        from . import _prepare_data
        from .rdf import merge_graph

        target = self.data_graph if self.inplace else self.data_graph.clone()
        schema = _prepare_data(Graph(), None, self.ont_graph, None, None, False)
        destination = (
            target.impl.graph(URIRef("urn:pyshacl:inoculation"))
            if self.data_graph_is_multigraph
            else target.impl
        )
        merge_graph(destination, schema)
        return target

    def _prepare_target(self, rules=False):
        from . import _prepare_data
        from .rdf import merge_graph

        if self.options.get("use_js"):
            raise NotImplementedError("Unsupported SHACL-JS")
        if self.options.get("sparql_mode"):
            raise NotImplementedError("Remote SPARQL validation is not implemented")
        if self._target_graph is not None:
            return self._target_graph
        inference = None if self.pre_inferenced else self.options.get("inference")
        modifies = (
            rules
            or self.options.get("advanced")
            or self.ont_graph is not None
            or (inference not in (None, "none"))
        )
        if self.ont_graph is not None:
            target = self.mix_in_ontology()
        else:
            target = self.data_graph.clone() if modifies and not self.inplace else self.data_graph
        if not modifies and (not self.inplace):
            self.inplace = True
        prepared = _prepare_data(target.impl, None, None, None, inference, False)
        if prepared is not target.impl:
            merge_graph(target.impl, prepared)
        if inference not in (None, "none"):
            self.pre_inferenced = True
        self._target_graph = target
        return target
