"""Run in an isolated wheel environment with only declared runtime dependencies."""

import warnings
from importlib.util import find_spec

import pyshacl_turbo as turbo
from rdflib import Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SH, XSD

assert find_spec("pyshacl") is None
assert find_spec("owlrl") is None
ex = Namespace("https://example.com/")
data, shapes = Graph(), Graph()
data.add((ex.s, ex.p, Literal("value")))
data.add((ex.s, ex.p, Literal("value", datatype=XSD.string)))
shapes.add((ex.S, SH.targetNode, ex.s))
shapes.add((ex.S, SH.path, ex.p))
shapes.add((ex.S, SH.maxCount, Literal(1)))
assert not turbo.validate(data, shacl_graph=shapes)[0]
assert set(turbo.load_from_source(data.serialize(format="turtle"))) == set(data)

data = Dataset(default_union=True)
source = data.graph(ex.source)
source.add((ex.s, RDF.type, ex.Child))
source.add((ex.Child, RDFS.subClassOf, ex.Parent))
before = set(source)
shapes = Graph()
shapes.add((ex.S, SH.targetNode, ex.s))
shapes.add((ex.S, SH["class"], ex.Parent))
assert turbo.validate(data, shacl_graph=shapes, inference="rdfs", inplace=True)[0]
assert set(source) == before
assert (ex.s, RDF.type, ex.Parent) in data.graph(URIRef("urn:pyshacl:inference"))

shapes.remove((ex.S, SH["class"], None))
shapes.add((ex.S, SH.node, ex.S))
with warnings.catch_warnings(record=True) as emitted:
    warnings.simplefilter("always", turbo.ShapeRecursionWarning)
    assert turbo.validate(data, shacl_graph=shapes)[0]
assert sum(issubclass(w.category, turbo.ShapeRecursionWarning) for w in emitted) == 1
print("Installed wheel passes identity, inference and recursion checks without pySHACL/owlrl.")
