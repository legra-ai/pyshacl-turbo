import pyoxigraph as ox
import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Literal
from rdflib.namespace import XSD
from test_compatibility import EX, graph


@pytest.mark.parametrize("store", [False, True])
@pytest.mark.parametrize(
    "actual, expected, matches",
    [
        (Literal("value", datatype=XSD.string), '"value"', True),
        (Literal("01", datatype=XSD.integer, normalize=False), "1", True),
        (Literal("value"), '"different"', False),
        (Literal("1"), "1", False),
    ],
)
def test_dash_inference_compares_literal_values(actual, expected, matches, store):
    data = graph("")
    data.add((EX.s, EX.p, actual))
    if store:
        target = ox.Store()
        target.load(input=data.serialize(format="nt"), format=ox.RdfFormat.N_TRIPLES)
        data = target
    shapes = graph(f"""@prefix dash: <http://datashapes.org/dash#>.
      @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
      ex:test a dash:InferencingTestCase; dash:expectedResult [
        rdf:subject ex:s; rdf:predicate ex:p; rdf:object {expected}].""")
    reference = pyshacl.validate(data, shacl_graph=shapes, check_dash_result=True)
    result = turbo.validate(data, shacl_graph=shapes, check_dash_result=True)
    assert reference[0] is matches
    assert result[0] is matches
