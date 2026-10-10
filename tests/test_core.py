"""Native Core regressions: reports, composition, paths and lexical semantics."""

import pyshacl_turbo as turbo
import pytest
from rdflib import Literal
from test_compatibility import EX, SH, compare, graph


@pytest.mark.parametrize(
    "constraint,values",
    [
        ("sh:class ex:C", 'ex:a, ex:b, "text"'),
        ("sh:datatype xsd:integer", '1, "wrong", ex:a'),
        ("sh:nodeKind sh:IRI", 'ex:a, "text", []'),
        ("sh:minExclusive 2", '1, 2, 3, "bad"'),
        ("sh:maxExclusive 2", '1, 2, 3, "bad"'),
        ("sh:minInclusive 2", '1, 2, 3, "bad"'),
        ("sh:maxInclusive 2", '1, 2, 3, "bad"'),
        ("sh:minLength 2", '"a", "éx", []'),
        ("sh:maxLength 2", '"a", "abc", []'),
        ('sh:pattern "^a"; sh:flags "i"', '"Abc", "no", []'),
        ('sh:languageIn ("en")', '"a"@en, "b"@en-GB, "c"@fr, "d"'),
        ('sh:in (ex:a "yes")', 'ex:a, "yes", "no"'),
        ("sh:uniqueLang true", '"a"@en, "b"@en, "c"@fr'),
        ("sh:equals ex:q", "ex:a, ex:b"),
        ("sh:disjoint ex:q", "ex:a, ex:b"),
        ("sh:lessThan ex:n", "1, 4, 6"),
        ("sh:lessThanOrEquals ex:n", "1, 4, 6"),
    ],
)
def test_core_differential(constraint, values):
    compare(
        graph(
            f"ex:s ex:p {values}; ex:q ex:b, ex:c; ex:n 3, 4. ex:a a ex:Sub. ex:Sub rdfs:subClassOf ex:C."
        ),
        graph(f'ex:P sh:targetNode ex:s; sh:path ex:p; {constraint}; sh:message "invalid".'),
    )


@pytest.mark.parametrize("operator", ["node", "not", "and", "or", "xone"])
def test_shape_composition_reports(operator):
    expression = "ex:C" if operator in {"node", "not"} else "(ex:C ex:D)"
    compare(
        graph('ex:s ex:p 1, "hello", ex:a.'),
        graph(f"""ex:P sh:targetNode ex:s; sh:path ex:p; sh:{operator} {expression}; sh:message "parent".
            ex:C sh:datatype xsd:integer; sh:message "integer".
            ex:D sh:nodeKind sh:Literal; sh:message "literal"."""),
    )


@pytest.mark.parametrize(
    "path",
    [
        "(ex:p ex:q)",
        "[sh:inversePath ex:p]",
        "[sh:alternativePath (ex:p ex:q)]",
        "[sh:zeroOrMorePath ex:p]",
        "[sh:oneOrMorePath ex:p]",
        "[sh:zeroOrOnePath ex:p]",
        "[sh:inversePath (ex:p [sh:zeroOrMorePath ex:q])]",
    ],
)
def test_paths_include_cycles_and_unique_values(path):
    compare(
        graph("ex:a ex:p ex:b, ex:c. ex:b ex:p ex:a; ex:q ex:d. ex:c ex:p ex:d; ex:q ex:d."),
        graph(f'ex:P sh:targetNode ex:a; sh:path {path}; sh:maxCount 0; sh:message "values".'),
    )


@pytest.mark.parametrize(
    "path",
    [
        "[]",
        "(ex:p)",
        "[sh:alternativePath (ex:p)]",
        "[sh:inversePath ex:p, ex:q]",
        "[sh:inversePath ex:p; sh:zeroOrMorePath ex:q]",
        '"literal"',
    ],
)
def test_invalid_paths_fail_at_compile_time(path):
    with pytest.raises(ValueError):
        turbo.compile_shapes(graph(f"ex:P sh:path {path}; sh:minCount 1."))


def test_cyclic_path_definition_is_a_hard_error():
    with pytest.raises(ValueError, match="[Cc]ycl"):
        turbo.compile_shapes(graph("ex:P sh:path _:path. _:path sh:inversePath _:path."))


def test_closed_report_uses_offending_predicate_and_value():
    compare(
        graph("ex:s ex:p 1; ex:q 2; a ex:C."),
        graph(
            """ex:S sh:targetNode ex:s; sh:closed true; sh:ignoredProperties (rdf:type);
            sh:property ex:P; sh:message "closed". ex:P sh:path ex:p.""".replace(
                "rdf:type", "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
            )
        ),
    )


def test_qualified_disjoint_counts_use_sibling_shapes():
    compare(
        graph('ex:s ex:p 1, "x", ex:a.'),
        graph("""ex:S sh:targetNode ex:s; sh:property ex:P, ex:Q.
            ex:P sh:path ex:p; sh:qualifiedValueShape ex:C; sh:qualifiedMinCount 1;
                sh:qualifiedValueShapesDisjoint true; sh:message "qualified".
            ex:Q sh:path ex:p; sh:qualifiedValueShape ex:D; sh:qualifiedMinCount 0.
            ex:C sh:datatype xsd:integer. ex:D sh:nodeKind sh:Literal."""),
    )


def test_invalid_integer_lexical_form_is_a_violation():
    data = graph("")
    data.add(
        (
            EX.s,
            EX.p,
            Literal("bad", datatype="http://www.w3.org/2001/XMLSchema#integer", normalize=False),
        )
    )
    compare(
        data,
        graph(
            'ex:P sh:targetNode ex:s; sh:path ex:p; sh:datatype xsd:integer; sh:message "integer".'
        ),
    )


def test_nested_node_details_are_retained():
    _, report, _ = compare(
        graph('ex:s ex:p "wrong".'),
        graph("""
        ex:P sh:targetNode ex:s; sh:path ex:p; sh:node ex:C; sh:message "parent".
        ex:C sh:datatype xsd:integer; sh:message "child".
    """),
    )
    assert len(list(report.triples((None, SH.detail, None)))) == 1


def test_distinct_numeric_lexical_forms_survive_rules_counts_and_reports():
    data = graph("")
    values = {
        Literal("01", datatype="http://www.w3.org/2001/XMLSchema#integer", normalize=False),
        Literal("1", datatype="http://www.w3.org/2001/XMLSchema#integer", normalize=False),
        Literal("300", datatype="http://www.w3.org/2001/XMLSchema#byte", normalize=False),
        Literal("4.0", datatype="http://www.w3.org/2001/XMLSchema#decimal", normalize=False),
    }
    for value in values:
        data.add((EX.s, EX.p, value))
    shapes = graph("""ex:P sh:targetNode ex:s; sh:path ex:p; sh:maxCount 3;
        sh:in (); sh:message "all values".
        ex:S sh:targetNode ex:s; sh:rule ex:R.
        ex:R a sh:SPARQLRule; sh:construct "CONSTRUCT { $this <https://example.com/q> ?v } WHERE { $this <https://example.com/p> ?v }".
    """)
    _, report, _ = turbo.validate(data, shacl_graph=shapes, advanced=True, inplace=True)
    assert set(report.objects(None, SH.value)) == values
    assert set(data.objects(EX.s, EX.q)) == values
    assert len(list(report.objects(None, SH.result))) == 5
