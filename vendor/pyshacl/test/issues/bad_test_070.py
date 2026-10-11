from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDFS, SH

from pyshacl import validate


"""
https://github.com/RDFLib/pySHACL/issues/70
"""

data_text = """\
@prefix ns0: <http://www.opengis.net/ont/geosparql#> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix ns1: <http://qudt.org/schema/qudt/> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix geo:   <http://www.opengis.net/ont/geosparql#> .
@prefix sf:    <http://www.opengis.net/ont/sf#> .

<http://www.w3id.org/afarcloud/pCoord?lat=45.75&amp;long=4.85>
  ns0:asWKT "POINT(45.75 4.85)"^^ns0:wktLiteral ;
  a <http://www.opengis.net/ont/sf#Point> .

<http://www.w3id.org/afarcloud/poi?lat=45.75&amp;long=4.85>
  ns0:hasGeometry <http://www.w3id.org/afarcloud/pCoord?lat=45.75&amp;long=4.85> ;
  a ns0:Feature .

<urn:afc:AS09:cropsManagement:TEC:soil:sen0022> a <https://json-ld.org/playground/AfarcloudSensors>, <https://json-ld.org/playground/SoilSensor> .
<urn:afc:AS09:sen0022:obs-1514810172/q1>
  dc:identifier "q1" ;
  ns1:numericValue "0.27121272683143616" ;
  ns1:unit <http://qudt.org/vocab/unit/DEG_C> ;
  a ns1:QuantityValue .

<urn:afc:AS09:sen0022:obs-1514810172>
  a sosa:Observation ;
  sosa:hasFeatureOfInterest <http://www.w3id.org/afarcloud/poi?lat=45.75&amp;long=4.85> ;
  sosa:hasResult <urn:afc:AS09:sen0022:obs-1514810172/q1> ;
  sosa:madeBySensor <urn:afc:AS09:cropsManagement:TEC:soil:sen0022> ;
  sosa:observedProperty <http://www.w3id.org/afarcloud/soil_temperature> ;
  sosa:resultTime "2018-01-01T12:36:12Z"^^xsd:dateTime .
"""
shacl_url = (
    "https://raw.githubusercontent.com/rapw3k/DEMETER/"
    "94762b9b0645f3b97dee675b15ee6278145a818b/models/SHACL/demeterAgriProfile-SHACL.ttl"
)


def test_070():
    g = Graph().parse(data=data_text, format="turtle")
    options = dict(
        shacl_graph=shacl_url,
        shacl_graph_format="turtle",
        abort_on_error=False,
        meta_shacl=False,
        debug=True,
        advanced=True,
    )
    geo = Namespace("http://www.opengis.net/ont/geosparql#")
    sf = Namespace("http://www.opengis.net/ont/sf#")
    conforms, report, _ = validate(g, **options)
    # The input supplies sf:Point, but no Geometry type or subclass relationship.
    assert not conforms
    (result,) = report.objects(None, SH.result)
    assert report.value(result, SH.sourceConstraintComponent) == SH.ClassConstraintComponent
    assert report.value(result, SH.resultPath) == geo.hasGeometry
    assert report.value(result, SH.focusNode) == URIRef(
        "http://www.w3id.org/afarcloud/poi?lat=45.75&amp;long=4.85"
    )
    assert report.value(result, SH.value) == URIRef(
        "http://www.w3id.org/afarcloud/pCoord?lat=45.75&amp;long=4.85"
    )

    # Supplying the missing relationship must resolve the violation.
    g.add((sf.Point, RDFS.subClassOf, geo.Geometry))
    conforms, report, _ = validate(g, **options)
    assert conforms
    assert not list(report.objects(None, SH.result))


if __name__ == "__main__":
    test_070()
