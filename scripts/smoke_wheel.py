"""Run in an isolated wheel environment with only declared runtime dependencies."""

import sys
import warnings
from importlib.resources import files
from importlib.util import find_spec
from xml.dom.minidom import DocumentFragment

import pyshacl_turbo as turbo
from rdflib import Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SH, XSD

assert find_spec("pyshacl") is None
assert find_spec("owlrl") is None
assert find_spec("pytest") is None

# Retained RDFLib 7.6 / pySHACL 0.40.1 Graph oracle, without their test extras.
html_data = Graph().parse(
    data='<urn:s> <urn:p> "<p>Hello</p>"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#HTML> .',
    format="turtle",
)
html_shapes = Graph().parse(
    data="""@prefix sh:<http://www.w3.org/ns/shacl#>.
    <urn:S> a sh:PropertyShape; sh:targetNode <urn:s>;
      sh:path <urn:p>; sh:nodeKind sh:IRI.""",
    format="turtle",
)
html_before = set(html_data)
html_conforms, html_report, _ = turbo.validate(html_data, shacl_graph=html_shapes)
assert html_conforms is False
html_value = next(html_report.objects(None, SH.value))
assert str(html_value) == "<p>Hello"
assert html_value.datatype == RDF.HTML and html_value.language is None
assert html_value.ill_typed is False
assert type(html_value.value) is DocumentFragment
assert [child.toxml() for child in html_value.value.childNodes] == ["<p>Hello</p>"]
assert set(html_data) == html_before

ex = Namespace("https://example.com/")
assert files(turbo).joinpath("py.typed").is_file()
target_shapes = Graph()
target_shapes.add((ex.Target, SH.targetNode, ex.s))
target_program = turbo.compile_shapes(target_shapes)
target_snapshot = turbo.prepare_target_data(Graph())
assert target_program.targeting(target_snapshot, ex.s) == [ex.Target]
assert target_program.targeting(target_snapshot, ex.s) == [ex.Target]
assert target_program.targeting(target_snapshot, ex.s, skip={ex.Target}) == []
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

data, shapes = Graph(), Graph()
shapes.add((ex.S, SH.targetNode, ex.s))
shapes.add((ex.S, SH.path, ex.p))
shapes.add((ex.S, SH.pattern, Literal(r"(?i)^(?P<letter>i)-(?P=letter)(?=$)")))
program = turbo.compile_shapes(shapes)
for value, conforms in [("i-İ", True), ("i-ı", False), ("I-i", True)]:
    data.set((ex.s, ex.p, Literal(value)))
    assert program.validate(data)[0] is conforms
print(
    "Installed wheel passes HTML, identity, inference, recursion and regex checks "
    "without pySHACL/owlrl/pytest."
)

if sys.argv[1:]:
    assert sys.argv[1:] == ["--oxigraph"]
    from pyoxigraph import RdfFormat, Store

    store = Store()
    store.load(input='<urn:s> <urn:p> "value" .', format=RdfFormat.N_TRIPLES)
    shapes = Graph().parse(
        data="""@prefix sh: <http://www.w3.org/ns/shacl#> .
        <urn:S> sh:targetNode <urn:s>; sh:property [sh:path <urn:p>; sh:minCount 1].""",
        format="turtle",
    )
    program = turbo.compile_shapes(shapes)
    assert turbo.validate(store, shacl_graph=shapes)[0]
    assert program.validate(store)[0]
    store.clear()
    assert not turbo.validate(store, shacl_graph=shapes)[0]
    assert not program.validate(store)[0]
    print("Optional PyOxigraph Store input passes valid and invalid cases, including shape reuse.")
