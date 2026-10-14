"""RDFLib-facing shape inspection; targeting executes in Rust."""

import logging
from decimal import Decimal

from rdflib.namespace import RDF, RDFS, SH

from .target_data import prepare_target_data


class Shape:
    def __init__(self, sg, node, p=False, path=None, logger=None):
        self.sg = sg
        self.node = node
        self._p = p
        self._path = path
        self._advanced = False
        self.logger = logger or logging.getLogger(__name__)

    @property
    def is_property_shape(self):
        return self._p

    @property
    def deactivated(self):
        return bool(self.sg.graph.value(self.node, SH.deactivated))

    @property
    def severity(self):
        return self.sg.graph.value(self.node, SH.severity, default=SH.Violation)

    @property
    def message(self):
        return iter(set(self.objects(SH.message)))

    @property
    def name(self):
        return iter(set(self.objects(SH.name)))

    @property
    def description(self):
        return iter(set(self.objects(SH.description)))

    @property
    def order(self):
        return Decimal(str(self.sg.graph.value(self.node, SH.order, default=0)))

    def objects(self, predicate):
        return self.sg.objects(self.node, predicate)

    def path(self):
        return self._path if self._p else None

    def property_shapes(self):
        return self.objects(SH.property)

    def get_other_shape(self, node):
        return self.sg.lookup_shape_from_node(node)

    def target_nodes(self):
        return self.objects(SH.targetNode)

    def target_classes(self):
        return self.objects(SH.targetClass)

    def target_objects_of(self):
        return self.objects(SH.targetObjectsOf)

    def target_subjects_of(self):
        return self.objects(SH.targetSubjectsOf)

    def implicit_class_targets(self):
        classes = set(self.sg.graph.subjects(RDFS.subClassOf, RDFS.Class)) | {RDFS.Class}
        return [self.node] if classes.intersection(self.objects(RDF.type)) else []

    def target(self):
        return (
            self.target_nodes(),
            self.target_classes(),
            self.implicit_class_targets(),
            self.target_objects_of(),
            self.target_subjects_of(),
        )

    def set_advanced(self, value):
        self._advanced = bool(value)

    def focus_nodes(self, data_graph, debug=False):
        data = prepare_target_data(data_graph)
        return data._focus_nodes(self.sg._compile(), self.node, self._advanced)
