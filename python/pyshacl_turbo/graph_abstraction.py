"""Live RDFLib graph views used by the public validation and rule runners.

The wrapper retains the caller's graph/store; it neither snapshots nor reasons.
Native I/O explicitly uses the underlying graph to preserve its real scope.
"""

from rdflib import Dataset, Graph, URIRef
from rdflib.plugins.sparql.operators import register_custom_function, unregister_custom_function


def _reject_native_store_graph(graph):
    while isinstance(graph, DataGraph):
        graph = graph.impl
    if getattr(graph, "_turbo_native_graph", False):
        raise NotImplementedError(
            "SHACL input through the native Store Graph facade is not implemented"
        )


class DataGraph(Dataset):
    def __new__(cls, store, impl=None, locked_context=None):
        return object.__new__(RdfLibDataGraph if cls is DataGraph else cls)

    @classmethod
    def from_rdflib_graph(cls, graph):
        return cls(graph.store, impl=graph)

    @classmethod
    def from_rdflib_dataset(cls, dataset):
        return cls(dataset.store, impl=dataset)

    @classmethod
    def from_rdflib(cls, source):
        _reject_native_store_graph(source)
        if not isinstance(source, Graph):
            raise ValueError("Invalid rdflib source type")  # noqa: TRY004 - reference API
        return cls(source.store, impl=source)


class RdfLibDataGraph(DataGraph):
    def __init__(self, store, impl=None, locked_context=None):
        self.impl = impl if impl is not None else Dataset(store=store)
        _reject_native_store_graph(self.impl)
        self._backing_store = store
        self.is_oxigraph = False
        self.is_multi_graph = isinstance(self.impl, Dataset)
        self._default_union = self.impl.default_union if self.is_multi_graph else False
        super().__init__(store=store, default_union=self._default_union)
        if isinstance(locked_context, Graph):
            self.locked_context = locked_context
        elif isinstance(locked_context, str):
            self.locked_context = self.get_context(locked_context)
        else:
            self.locked_context = None

    @property
    def identifier(self):
        if self.is_multi_graph:
            return (
                self.locked_context.identifier
                if self.locked_context is not None
                else "RDFLibDataset"
            )
        return str(self.impl.identifier)

    @property
    def store(self):
        return self._backing_store

    # Reference DataGraph deliberately removes RDFLib's inherited setters.
    @property  # type: ignore[misc]
    def namespace_manager(self):
        return self.impl.namespace_manager

    @property  # type: ignore[misc]  # Same read-only reference contract as above.
    def default_graph(self):
        return self.impl.default_graph if self.is_multi_graph else self.impl

    @property
    def default_union(self):
        return self._default_union

    @default_union.setter
    def default_union(self, value):
        self._default_union = value
        if isinstance(self.impl, Dataset):
            self.impl.default_union = value

    def is_multigraph(self):
        return self.is_multi_graph

    @property
    def _view(self):
        return self.locked_context if self.locked_context is not None else self.impl

    def triples(self, triple):
        yield from self._view.triples(triple)

    def quads(self, quad=None):
        if self.is_multi_graph:
            yield from self.impl.quads(quad)
        else:
            triple = (None, None, None) if quad is None else quad[:3]
            for s, p, o in self._view.triples(triple):
                yield s, p, o, self._view.identifier

    def graphs(self, triple=None):
        if self.is_multi_graph:
            yield from self.impl.graphs(triple)
        else:
            yield self.impl

    contexts = graphs

    def add(self, triple):
        return self._view.add(triple)

    def remove(self, triple):
        return self._view.remove(triple)

    def __contains__(self, triple):
        return triple in self._view

    def __len__(self):
        return len(self._view)

    def objects(self, subject=None, predicate=None, unique=False):
        subjects = subject if isinstance(subject, (list, tuple)) else [subject]
        for item in subjects:
            yield from self._view.objects(item, predicate, unique=unique)

    def subjects(self, predicate=None, object=None, unique=False):
        objects = object if isinstance(object, (list, tuple)) else [object]
        for item in objects:
            yield from self._view.subjects(predicate, item, unique=unique)

    def predicate_objects(self, subject=None, unique=False):
        return self._view.predicate_objects(subject, unique=unique)

    def subject_objects(self, predicate=None, unique=False):
        return self._view.subject_objects(predicate, unique=unique)

    def subject_predicates(self, object=None, unique=False):
        return self._view.subject_predicates(object, unique=unique)

    def transitive_objects(self, subject, predicate, remember=None):
        return self._view.transitive_objects(subject, predicate, remember=remember)

    def transitive_subjects(self, predicate, object, remember=None):
        return self._view.transitive_subjects(predicate, object, remember=remember)

    def items(self, list):
        return self._view.items(list)

    def bind(self, prefix, namespace, **kwargs):
        return self.impl.bind(prefix, namespace, **kwargs)

    def query(self, *args, **kwargs):
        return self.impl.query(*args, **kwargs)

    def get_context(self, identifier):
        return self.impl.graph(URIRef(identifier)) if self.is_multi_graph else self.impl

    def with_locked_context(self, identifier):
        if not self.is_multi_graph:
            raise ValueError("Cannot create a locked context on a non-dataset graph")
        context = self.get_context(identifier)
        return RdfLibDataGraph(context.store, context, context)

    def clone(self, destination=None, identifier=None):
        _reject_native_store_graph(self)
        from .rdf import merge_graph

        if destination is not None:
            result = destination
        elif self.is_multi_graph:
            result = Dataset(default_union=self.impl.default_union)
            result.default_graph = result.graph(self.impl.default_graph.identifier)
        else:
            selected = self.impl.identifier if identifier is None else identifier
            result = Graph(identifier=selected)
        result = merge_graph(result, self.impl)
        for prefix, namespace in self.impl.namespaces():
            result.bind(prefix, namespace)
        return DataGraph.from_rdflib(result)

    def register_custom_function(
        self,
        function_name,
        rdflib_fn,
        oxigraph_fn=None,
        override=False,
        raw=False,
        is_aggregate=False,
    ):
        register_custom_function(function_name, rdflib_fn, override, raw)

    def unregister_custom_function(self, function_name, rdflib_fn, oxigraph_fn=None):
        unregister_custom_function(function_name, rdflib_fn)
