"""Invalid executable SHACL declarations must fail during compilation."""

import pyshacl_turbo as turbo
import pytest
from rdflib import Graph


@pytest.mark.parametrize(
    "declaration",
    [
        "sh:order ex:notNumeric",
        'sh:order "invalid"^^xsd:decimal',
        'sh:class "not an IRI"',
        'sh:datatype "not an IRI"',
        "sh:nodeKind ex:UnsupportedKind",
        "sh:minExclusive ex:notLiteral",
        "sh:maxInclusive ex:notLiteral",
        "sh:minCount ex:notLiteral",
        "sh:maxCount 1, 2",
        'sh:minLength "invalid"',
        "sh:languageIn (ex:notString)",
        "sh:pattern ex:notLiteral",
        'sh:pattern "a"; sh:flags ex:notLiteral',
        'sh:uniqueLang "invalid"',
        'sh:closed "invalid"',
        "sh:closed true; sh:ignoredProperties (1)",
        'sh:equals "not an IRI"',
        "sh:lessThan [sh:inversePath ex:p]",
        "sh:property ex:MissingPath",
        "sh:sparql [sh:select 1]",
        'sh:sparql [sh:select "ASK {}"]',
        "sh:target [a sh:SPARQLTarget]",
        "sh:target [a sh:SPARQLTarget; sh:select 1]",
        'sh:target [a sh:SPARQLTarget; sh:select "ASK {}"]',
        'sh:target [a sh:SPARQLTarget; sh:select "SELECT ?wrong WHERE {}"]',
        "sh:target [a ex:UnknownTarget]",
        "sh:rule [a sh:SPARQLRule]",
        "sh:rule [a sh:SPARQLRule; sh:construct 1]",
        'sh:rule [a sh:SPARQLRule; sh:construct "SELECT ?this WHERE {}"]',
        "sh:rule [a sh:TripleRule; sh:subject sh:this; sh:predicate ex:p]",
        "sh:rule [a ex:UnsupportedRule]",
        "sh:expression [sh:filterShape ex:Check]",
        "sh:expression [ex:unknown ()]",
        "sh:misspelledConstraint true",
    ],
)
def test_invalid_executable_declarations_fail_before_use(declaration):
    source = f"""@prefix sh: <http://www.w3.org/ns/shacl#>.
    @prefix ex: <https://example.org/>.
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
    ex:S a sh:NodeShape; sh:targetNode ex:s; {declaration}.
    """
    with pytest.raises((ValueError, NotImplementedError)):
        turbo.compile_shapes(Graph().parse(data=source, format="turtle"), advanced=True)
