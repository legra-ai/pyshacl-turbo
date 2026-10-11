"""SPARQL regular expressions must follow the pinned RDFLib/pySHACL behavior."""

import re
from concurrent.futures import ThreadPoolExecutor

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Literal, Namespace
from rdflib.namespace import RDF, XSD
from test_compatibility import EX, SH, compare, graph, reference_rules


def constraint(expression):
    shapes = graph("ex:S sh:targetNode ex:s; sh:sparql ex:C. ex:C sh:message 'Mismatch'.")
    shapes.add(
        (
            EX.C,
            SH.select,
            Literal(
                f"SELECT $this ?value WHERE {{ $this <{EX.p}> ?value . FILTER({expression}) }}"
            ),
        )
    )
    return shapes


@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize(
    "pattern,flags,values",
    [
        (r"foo(?=bar)", "", ["foobar", "foobaz"]),
        (r"(?<=foo)bar", "", ["foobar", "bazbar"]),
        (r"^(\w+)-\1$", "", ["café-café", "a-b"]),
        (r"^(?P<word>\w+)-(?P=word)$", "", ["same-same", "one-two"]),
        (r"^(a)?(?(1)b|c)$", "", ["ab", "c", "ac"]),
        (r"^(?>a|ab)c$", "", ["ac", "abc"]),
        (r"^abc$", "", ["abc\n", "abc\n\n", "abc"]),
        (r"^abc$", "I", ["abc", "ABC"]),
        (r"^a.b$", "s", ["a\nb", "ab"]),
        (r"^abc$", "m", ["x\nabc\ny", "ABC"]),
        (r"^a b$", "x", ["a b", "ab"]),
        (r"a.b", "q", ["axb", "a.b", "ab"]),
        (r"^\w+$", "", ["²", "a\u0301", "café"]),
        (r"^\s$", "", ["\x1c", "x"]),
        (r"\b²\b", "", ["²", "x²"]),
        (r"^i$", "i", ["İ", "ı", "x"]),
        (r"(?ai)^é$", "", ["é", "É"]),
        (r"^a{,2}b$", "", ["b", "aab", "aaab"]),
        ("(?x)^ a # comment\n b $", "", ["a", "ab"]),
    ],
)
def test_sparql_regex_reports_match_reference(pattern, flags, values, dynamic):
    data = graph("")
    for value in values:
        data.add((EX.s, EX.p, Literal(value)))
    if dynamic:
        shapes = constraint("!REGEX(?value, ?pattern, ?flags)")
        query = str(shapes.value(EX.C, SH.select)).replace(
            "FILTER(", f"$this <{EX.pattern}> ?pattern; <{EX.flags}> ?flags . FILTER("
        )
        shapes.set((EX.C, SH.select, Literal(query)))
        data.add((EX.s, EX.pattern, Literal(pattern)))
        data.add((EX.s, EX.flags, Literal(flags)))
    else:
        shapes = constraint(f"!REGEX(?value, {Literal(pattern).n3()}, {Literal(flags).n3()})")
    compare(data, shapes)


@pytest.mark.parametrize(
    "pattern,replacement,flags,text",
    [
        (r"(?<=foo)bar", "new", "", "foobar bar"),
        (r"(\w+)-(\w+)", "$2/$1", "", "one-two"),
        (r"(?P<word>\w+)", r"\g<word>/", "", "café"),
        (r"(a)?b", "<$1>", "", "b ab"),
        (r"(a)", "$0", "", "a"),
        (r"(a)", "$$1", "", "a"),
        (r"(a)", r"\n$1\t", "", "a"),
        (r"(a)", "$123", "", "a"),
        (r"^i$", "match", "i", "İ"),
        (r"a.b", "match", "s", "a\nb"),
        (r"a.b", "match", "q", "axb"),
        (r"x*", "-", "", "abxd"),
        (r".*?", "-", "", "ab"),
        (r"|a", "-", "", "ab"),
        (r"a*", "-", "", "éa"),
        (r"", "-", "", "é"),
        (r"", "-", "", ""),
        (r"a", "x", "i", "aaaa"),
        (r"a", "x", "m", "a" * 12),
        (r"a", "x", "s", "a" * 20),
        (r"(?i)a", "x", "", "Aaa"),
        (r"(?=a)", "-", "", "aab"),
        (r"(?P<first>a)(b)", "$2$1", "", "ab"),
        (r"(?P<é>é)", r"\g<é>", "", "é"),
    ],
)
def test_sparql_replace_rule_output_matches_reference(pattern, replacement, flags, text):
    data = graph("")
    data.add((EX.s, EX.p, Literal(text)))
    shapes = graph("ex:S sh:targetNode ex:s; sh:rule ex:R. ex:R a sh:SPARQLRule.")
    shapes.add(
        (
            EX.R,
            SH.construct,
            Literal(
                f"CONSTRUCT {{ $this <{EX.result}> ?result }} WHERE {{ $this <{EX.p}> ?text . "
                f"BIND(REPLACE(?text, {Literal(pattern).n3()}, {Literal(replacement).n3()}, {Literal(flags).n3()}) AS ?result) }}"
            ),
        )
    )
    expected = reference_rules(data, shapes)
    actual = turbo.shacl_rules(data, shacl_graph=shapes, advanced=True)
    assert set(actual) == set(expected)


@pytest.mark.parametrize("expression", ['REGEX(?value, "(")', 'REPLACE(?value, "a", "$2") = "x"'])
def test_sparql_pattern_errors_are_hard_errors(expression):
    shapes = constraint(expression)
    for validate in (pyshacl.validate, turbo.validate):
        with pytest.raises((re.error, ValueError, RuntimeError)):
            validate(graph('ex:s ex:p "a".'), shacl_graph=shapes, advanced=True)


@pytest.mark.parametrize(
    "source", [Literal("ab"), Literal("ab", lang="en"), Literal("ab", datatype=XSD.string)]
)
@pytest.mark.parametrize("constant", [False, True])
def test_sparql_replace_preserves_literal_identity(source, constant):
    data = graph("")
    data.add((EX.s, EX.p, source))
    argument = source.n3() if constant else "?text"
    shapes = graph("ex:S sh:targetNode ex:s; sh:rule ex:R. ex:R a sh:SPARQLRule.")
    shapes.add(
        (
            EX.R,
            SH.construct,
            Literal(
                f"CONSTRUCT {{ $this <{EX.result}> ?result }} WHERE {{ $this <{EX.p}> ?text . "
                f'BIND(REPLACE({argument}, "a", "x") AS ?result) }}'
            ),
        )
    )
    assert set(turbo.shacl_rules(data, shacl_graph=shapes)) == set(reference_rules(data, shapes))


def test_native_function_preserves_argument_lexical_identity():
    data = graph("")
    data.add((EX.s, EX.p, Literal("01", datatype=XSD.integer, normalize=False)))
    shapes = graph("""ex:identity a sh:SPARQLFunction; sh:parameter [sh:path ex:arg];
      sh:select "SELECT ?arg WHERE {}".
      ex:S sh:targetNode ex:s; sh:rule [a sh:SPARQLRule;
      sh:construct "CONSTRUCT { $this <https://example.com/result> ?result } WHERE { $this <https://example.com/p> ?value . BIND(ex:identity(?value) AS ?result) }"] .""")
    assert set(turbo.shacl_rules(data, shacl_graph=shapes)) == set(reference_rules(data, shapes))


@pytest.mark.parametrize("template", [r"\q", "$99", r"\g<missing>", "\\", r"\400", r"\g<>"])
def test_invalid_replace_templates_raise_even_without_a_match(template):
    shapes = constraint(f'REPLACE(?value, "not-present", {Literal(template).n3()}) = "x"')
    for validate in (pyshacl.validate, turbo.validate):
        with pytest.raises((re.error, IndexError, ValueError, RuntimeError)):
            validate(graph('ex:s ex:p "a".'), shacl_graph=shapes, advanced=True)


@pytest.mark.parametrize(
    "query",
    [
        'SELECT (REGEX("ab", "(?<=a)b") AS ?result) WHERE {}',
        'SELECT ?value WHERE { ex:s ex:p ?value FILTER EXISTS { FILTER(REGEX(?value, "(?<=a)b")) } }',
        'SELECT ?value ?result WHERE { ex:s ex:p ?value OPTIONAL { FILTER(REGEX(?value, "(?<=a)b")) BIND(true AS ?result) } } ORDER BY ?value',
        'SELECT (COUNT(REGEX(?value, "(?<=a)b")) AS ?result) WHERE { ex:s ex:p ?value }',
        'SELECT ?value WHERE { ex:s ex:p ?value } ORDER BY DESC(REGEX(?value, "(?<=a)b")) ?value',
        'SELECT ?value WHERE { { SELECT ?value WHERE { ex:s ex:p ?value FILTER(REGEX(?value, "(?<=a)b")) } } }',
        'SELECT ?value WHERE { { ex:s ex:p ?value FILTER(REGEX(?value, "(?<=a)b")) } UNION { ex:s ex:p ?value FILTER(REGEX(?value, "^no$")) } } ORDER BY ?value',
        'SELECT (COALESCE(REGEX(42, "a"), true) AS ?result) WHERE {}',
        'SELECT (IF(true, true, REGEX("a", "(")) AS ?result) WHERE {}',
        'SELECT (REGEX("ab"@en, "(?<=a)b"@en) AS ?result) WHERE {}',
        'SELECT (REPLACE("ab"@en, "a"@en, "x"@en) AS ?result) WHERE {}',
        'SELECT (REPLACE(REPLACE("ab"^^xsd:string, "a", "x"), "b", "y") AS ?result) WHERE {}',
        'SELECT (STRLEN(REPLACE("ab", "a", "xyz")) AS ?result) WHERE {}',
        'SELECT ("REGEX( REPLACE(" AS ?result) WHERE {}',
        'SELECT ("value"^^xsd:string AS ?result) WHERE {}',
        'SELECT ?value WHERE { VALUES ?value { ex:iri "ab"@en UNDEF } }',
        r'SELECT (REGEX("a\nb", "a.b", false) AS ?result) WHERE {}',
        'SELECT (REPLACE("aaaaaaaaaaaaaaaaaaaa", "a", "b", false) AS ?result) WHERE {}',
    ],
)
def test_regex_builtins_in_nested_query_expressions(query):
    source = graph('ex:s ex:p "ab", "no".')
    expected = source.query(query).serialize(format="json").decode()
    dash = Namespace("http://datashapes.org/dash#")
    source.add((EX.case, RDF.type, dash.QueryTestCase))
    source.add((EX.case, SH.select, Literal(query)))
    source.add((EX.case, dash.expectedResult, Literal(expected)))
    assert turbo.evaluate_query_testcase(source, EX.case)[0]


def test_sparql_function_and_target_use_native_python_regex():
    data = graph('ex:s ex:p "ab". ex:other ex:p "no".')
    shapes = graph("""ex:check a sh:SPARQLFunction; sh:parameter [sh:path ex:arg];
      sh:select "SELECT (REGEX(?arg, '(?<=a)b') AS ?result) WHERE {}".
      ex:S a sh:PropertyShape; sh:target [a sh:SPARQLTarget;
        sh:select "SELECT ?this WHERE { ?this ex:p ?value FILTER(ex:check(?value)) }"];
      sh:path ex:missing; sh:minCount 1.""")
    assert not compare(data, shapes)[0]


@pytest.mark.parametrize(
    "component,bound,values",
    [
        ("minCount", 1, ""),
        ("minCount", 3, "ex:s ex:p 1, 2."),
        ("maxCount", 0, "ex:s ex:p 1."),
        ("maxCount", 1, "ex:s ex:p 1, 2."),
    ],
)
def test_default_cardinality_messages_match_reference(component, bound, values):
    shapes = graph(f"ex:S sh:targetNode ex:s; sh:path ex:p; sh:{component} {bound}.")
    assert not compare(graph(values), shapes)[0]


def test_sparql_pattern_errors_do_not_commit_rules():
    shapes = constraint('REGEX(?value, "(")')
    shapes += graph("""ex:Rule sh:targetNode ex:s; sh:rule [a sh:TripleRule;
      sh:subject sh:this; sh:predicate ex:derived; sh:object true].""")
    data = graph('ex:s ex:p "a".')
    before = set(data)
    with pytest.raises((ValueError, RuntimeError), match="SPARQL pattern"):
        turbo.validate(data, shacl_graph=shapes, advanced=True, inplace=True)
    assert set(data) == before


def test_compiled_regex_errors_are_isolated_across_calls_and_threads():
    shapes = constraint("!REGEX(?value, ?pattern)")
    query = str(shapes.value(EX.C, SH.select)).replace(
        "FILTER(", f"$this <{EX.pattern}> ?pattern . FILTER("
    )
    shapes.set((EX.C, SH.select, Literal(query)))
    program = turbo.compile_shapes(shapes, advanced=True)

    def run(invalid):
        data = graph('ex:s ex:p "ab".')
        data.add((EX.s, EX.pattern, Literal("(" if invalid else "(?<=a)b")))
        if invalid:
            with pytest.raises((ValueError, RuntimeError), match="SPARQL pattern"):
                program.validate(data)
        else:
            assert program.validate(data)[0]

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run, [True, False] * 12))


@pytest.mark.parametrize("replace", [False, True])
def test_sparql_backtracking_exhaustion_is_a_hard_error(replace):
    pattern = Literal(r"^(a|aa)+\1$").n3()
    expression = (
        f'REPLACE(?value, {pattern}, "x") = "x"' if replace else f"REGEX(?value, {pattern})"
    )
    data = graph("")
    data.add((EX.s, EX.p, Literal("a" * 40 + "!")))
    with pytest.raises(RuntimeError, match="matching failed.*[Bb]acktrack"):
        turbo.validate(data, shacl_graph=constraint(expression), advanced=True)
