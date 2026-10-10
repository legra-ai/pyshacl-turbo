import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib.compare import isomorphic
from rdflib.namespace import OWL, RDF
from test_compatibility import EX, PREFIXES, graph

PREFIX = PREFIXES + "@prefix owl: <http://www.w3.org/2002/07/owl#>. "


@pytest.mark.parametrize("mode", ["owlrl", "both"])
@pytest.mark.parametrize(
    "body,expected",
    [
        ("ex:p owl:inverseOf ex:q. ex:a ex:p ex:b.", (EX.b, EX.q, EX.a)),
        ("ex:p a owl:SymmetricProperty. ex:a ex:p ex:b.", (EX.b, EX.p, EX.a)),
        ("ex:p a owl:TransitiveProperty. ex:a ex:p ex:b. ex:b ex:p ex:c.", (EX.a, EX.p, EX.c)),
        ("ex:p owl:equivalentProperty ex:q. ex:a ex:p ex:b.", (EX.a, EX.q, EX.b)),
        ("ex:A owl:equivalentClass ex:B. ex:a a ex:A.", (EX.a, RDF.type, EX.B)),
        ("ex:p a owl:FunctionalProperty. ex:a ex:p ex:b, ex:c.", (EX.b, OWL.sameAs, EX.c)),
        (
            "ex:p a owl:InverseFunctionalProperty. ex:a ex:p ex:c. ex:b ex:p ex:c.",
            (EX.a, OWL.sameAs, EX.b),
        ),
        ("ex:R owl:onProperty ex:p; owl:hasValue ex:b. ex:a a ex:R.", (EX.a, EX.p, EX.b)),
        (
            "ex:R owl:onProperty ex:p; owl:someValuesFrom ex:B. ex:a ex:p ex:b. ex:b a ex:B.",
            (EX.a, RDF.type, EX.R),
        ),
        (
            "ex:R owl:onProperty ex:p; owl:allValuesFrom ex:B. ex:a a ex:R; ex:p ex:b.",
            (EX.b, RDF.type, EX.B),
        ),
        ("ex:C owl:intersectionOf (ex:A ex:B). ex:a a ex:A, ex:B.", (EX.a, RDF.type, EX.C)),
        ("ex:C owl:unionOf (ex:A ex:B). ex:a a ex:B.", (EX.a, RDF.type, EX.C)),
        ("ex:C owl:oneOf (ex:a ex:b).", (EX.a, RDF.type, EX.C)),
        (
            "ex:p owl:propertyChainAxiom (ex:q ex:r). ex:a ex:q ex:b. ex:b ex:r ex:c.",
            (EX.a, EX.p, EX.c),
        ),
        (
            "ex:C owl:hasKey (ex:p ex:q). ex:a a ex:C; ex:p 1; ex:q 2. ex:b a ex:C; ex:p 1; ex:q 2.",
            (EX.a, OWL.sameAs, EX.b),
        ),
    ],
)
def test_native_owlrl_entailments(mode, body, expected):
    data = turbo.load_from_source(PREFIX + body)
    turbo.validate(data, shacl_graph=graph(""), inference=mode, inplace=True)
    assert expected in data


def test_inference_never_imports_python_owlrl(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "owlrl", None)
    data = turbo.load_from_source(PREFIX + "ex:A owl:equivalentClass ex:B. ex:a a ex:A.")
    turbo.validate(data, shacl_graph=graph(""), inference="owlrl", inplace=True)
    assert (EX.a, RDF.type, EX.B) in data


@pytest.mark.parametrize("mode", ["owlrl", "both"])
@pytest.mark.parametrize("class_name", ["ex:C", "_:C"])
def test_keys_match_only_instances_of_the_declared_class(mode, class_name):
    data = turbo.load_from_source(
        PREFIX
        + f"""
      {class_name} owl:hasKey (ex:p ex:q).
      ex:a a {class_name}; ex:p 1; ex:q 2.
      ex:b a {class_name}; ex:p 1; ex:q 2.
      ex:c a ex:Other; ex:p 1; ex:q 2.
      ex:d a ex:Other; ex:p 1; ex:q 2.
    """
    )
    turbo.validate(data, shacl_graph=graph(""), inference=mode, inplace=True)
    people = {EX.a, EX.b, EX.c, EX.d}
    identities = {
        (s, o)
        for s, o in data.subject_objects(OWL.sameAs)
        if s in people and o in people and s != o
    }
    assert identities == {(EX.a, EX.b), (EX.b, EX.a)}


@pytest.mark.parametrize("mode", ["owlrl", "both"])
def test_empty_key_does_not_merge_class_instances(mode):
    data = turbo.load_from_source(
        PREFIX
        + """
      ex:C owl:hasKey (). ex:a a ex:C. ex:b a ex:C.
    """
    )
    turbo.validate(data, shacl_graph=graph(""), inference=mode, inplace=True)
    assert (EX.a, OWL.sameAs, EX.b) not in data


@pytest.mark.parametrize("mode", ["rdfs", "owlrl", "both"])
@pytest.mark.parametrize(
    "body",
    [
        "",
        "ex:A rdfs:subClassOf ex:B. ex:a a ex:A; ex:p ex:b.",
        "ex:A a owl:Class; owl:equivalentClass ex:B. ex:a a ex:A.",
        "ex:p a owl:ObjectProperty; rdfs:domain ex:A; rdfs:range ex:B. ex:a ex:p ex:b.",
        "ex:p owl:equivalentProperty ex:q. ex:a ex:p ex:b.",
        "ex:p a <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>.",
        "ex:a a xsd:byte. ex:b a xsd:token.",
    ],
)
def test_complete_inference_closure_without_literal_subjects(mode, body):
    expected = turbo.load_from_source(PREFIX + body)
    actual = turbo.load_from_source(PREFIX + body)
    pyshacl.validate(expected, shacl_graph=graph(""), inference=mode, inplace=True)
    turbo.validate(actual, shacl_graph=graph(""), inference=mode, inplace=True)
    assert isomorphic(actual, expected), {
        "missing": sorted(map(str, set(expected) - set(actual))),
        "extra": sorted(map(str, set(actual) - set(expected))),
    }


def test_key_requires_a_common_value_for_every_property():
    data = turbo.load_from_source(
        PREFIX
        + """
      ex:C owl:hasKey (ex:p ex:q).
      ex:a a ex:C; ex:p 1, 3; ex:q 2, 4.
      ex:b a ex:C; ex:p 3; ex:q 4, 5.
      ex:c a ex:C; ex:p 1; ex:q 6.
      ex:d a ex:C; ex:p 1.
    """
    )
    turbo.validate(data, shacl_graph=graph(""), inference="owlrl", inplace=True)
    assert (EX.a, OWL.sameAs, EX.b) in data
    for other in [EX.c, EX.d]:
        assert (EX.a, OWL.sameAs, other) not in data


@pytest.mark.parametrize("key", ['("bad")', "ex:Broken"])
def test_malformed_key_fails_without_committing_inference(key):
    data = turbo.load_from_source(PREFIX + f"ex:C owl:hasKey {key}. ex:a a ex:C.")
    before = set(data)
    with pytest.raises(ValueError):
        turbo.validate(data, shacl_graph=graph(""), inference="owlrl", inplace=True)
    assert set(data) == before


@pytest.mark.parametrize("named_individual", [False, True])
def test_ontology_imports_schema_and_explicit_named_individuals(named_individual):
    import pyshacl

    data = graph("ex:s ex:contact ex:c.")
    ontology = turbo.load_from_source(PREFIX + 'ex:c a ex:Contact; ex:email "c@example.com".')
    if named_individual:
        ontology.add((EX.c, RDF.type, OWL.NamedIndividual))
    shapes = graph("""ex:S sh:targetNode ex:s; sh:path ex:contact;
      sh:node [sh:class ex:Contact; sh:property [sh:path ex:email; sh:minCount 1]].""")
    expected = pyshacl.validate(data, shacl_graph=shapes, ont_graph=ontology, inference="rdfs")
    actual = turbo.validate(data, shacl_graph=shapes, ont_graph=ontology, inference="rdfs")
    assert actual[0] == expected[0] == named_individual
