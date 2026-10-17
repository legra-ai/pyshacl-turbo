import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, SH
from test_compatibility import EX, compare, graph


@pytest.mark.parametrize("property_shape", [False, True])
def test_class_violation_default_message_matches_reference(property_shape):
    target = "sh:targetNode ex:s; sh:path ex:p" if property_shape else "sh:targetNode ex:value"
    shapes = graph(f"ex:S {target}; sh:class ex:Required.")
    _, report, _ = compare(graph("ex:s ex:p ex:value. ex:value a ex:Other."), shapes)
    assert list(report.objects(None, SH.resultMessage)) == [
        Literal("Value does not have class ex:Required")
    ]


def test_issue70_missing_geometry_class_is_a_real_violation():
    # Reduced from bad_test_070's remote shape/data: no Geometry type or
    # Point-to-Geometry subclass statement is supplied.
    prefixes = """@prefix geo: <http://www.opengis.net/ont/geosparql#>.
      @prefix sf: <http://www.opengis.net/ont/sf#>."""
    data = graph(
        prefixes + "ex:place a geo:Feature; geo:hasGeometry ex:point. ex:point a sf:Point."
    )
    shapes = graph(
        prefixes
        + """ex:S sh:targetClass geo:Feature; sh:property ex:P.
      ex:P sh:path geo:hasGeometry; sh:class geo:Geometry."""
    )
    assert not compare(data, shapes)[0]
    data.add((EX.point, RDF.type, URIRef("http://www.opengis.net/ont/geosparql#Geometry")))
    assert pyshacl.validate(data, shacl_graph=shapes)[0]
    assert turbo.validate(data, shacl_graph=shapes)[0]


def test_multiple_classes_report_the_complete_declared_class_set():
    shapes = graph("ex:S sh:targetNode ex:value; sh:class ex:A, ex:B.")
    _, report, _ = compare(graph("ex:value a ex:A."), shapes)
    assert set(report.objects(None, SH.resultMessage)) == {
        Literal("Value class is not in classes (ex:A, ex:B)")
    }
