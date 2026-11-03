"""In-place public rules must write the insertion delta only once."""

import pyshacl_turbo as turbo
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, SH

EX = Namespace("urn:rule-delta:")


class ObservedGraph(Graph):
    def __init__(self):
        super().__init__()
        self.writes = []

    def add(self, triple):
        self.writes.append(triple)
        return super().add(triple)

    def addN(self, quads):
        def observed():
            for s, p, o, g in quads:
                self.writes.append((s, p, o))
                yield s, p, o, g

        return super().addN(observed())


def test_public_inplace_rules_write_only_new_triples_once():
    data = ObservedGraph()
    before = (EX.focus, RDF.type, EX.Person)
    added = (EX.focus, EX.added, Literal(True))
    data.add(before)
    shapes = Graph()
    for triple in [
        (EX.S, SH.targetNode, EX.focus),
        (EX.S, SH.rule, EX.rule),
        (EX.rule, RDF.type, SH.TripleRule),
        (EX.rule, SH.subject, SH.this),
        (EX.rule, SH.predicate, EX.added),
        (EX.rule, SH.object, Literal(True)),
    ]:
        shapes.add(triple)
    data.writes.clear()
    result = turbo.shacl_rules(data, shacl_graph=shapes, inplace=True)
    assert set(data) == {before, added}
    assert result.impl is data
    assert data.writes == [added]
