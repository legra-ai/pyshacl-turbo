import re

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Dataset, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, SH
from test_compatibility import EX, PREFIXES, graph


@pytest.mark.parametrize("kind", ["graph", "document", "dataset"])
def test_blank_node_text_uses_origin_graph_and_report_retains_inference(kind):
    text = PREFIXES + "[] a ex:Z; ex:p ex:o. ex:Z rdfs:subClassOf ex:A."
    data = graph("[] a ex:Z; ex:p ex:o. ex:Z rdfs:subClassOf ex:A.")
    if kind == "document":
        data = text
    elif kind == "dataset":
        dataset = Dataset(default_union=True)
        source = dataset.graph(EX.source)
        source += data
        data = dataset
    shapes = graph("""ex:S sh:targetClass ex:Z; sh:class ex:Required;
      sh:message "missing class".""")
    expected = pyshacl.validate(data, shacl_graph=shapes, inference="rdfs")
    actual = turbo.validate(data, shacl_graph=shapes, inference="rdfs")
    assert not actual[0] and not expected[0]
    assert isomorphic(actual[1], expected[1])
    for result in (expected, actual):
        focus_line = re.search(r"Focus Node:.*", result[2]).group()
        assert ("ex:A" in focus_line) == (kind == "graph")
        focus = next(result[1].objects(None, SH.focusNode))
        assert (focus, RDF.type, EX.A) in result[1]


def test_dataset_inference_uses_named_destination_without_changing_source():
    data = Dataset(default_union=True)
    original = data.graph(EX.source)
    original += graph("ex:a a ex:A. ex:A rdfs:subClassOf ex:B.")
    before = set(original)
    turbo.validate(data, shacl_graph=graph(""), inference="rdfs", inplace=True)
    assert set(original) == before
    inferred = data.graph(URIRef("urn:pyshacl:inference"))
    assert (EX.a, RDF.type, EX.B) in inferred
    assert (EX.a, RDF.type, EX.B) not in data.default_graph
