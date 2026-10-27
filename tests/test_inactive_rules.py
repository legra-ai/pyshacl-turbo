"""Inactive SHACL-AF rules do not change core validation or load rule bodies."""

import importlib

import pytest
from rdflib import Graph, URIRef
from rdflib.compare import isomorphic

PREFIX = "@prefix sh: <http://www.w3.org/ns/shacl#>. "
RULES = [
    "[a sh:TripleRule; sh:subject sh:this; sh:predicate <urn:added>; sh:object true]",
    "[a sh:TripleRule]",
    "[a sh:SPARQLRule; sh:construct 'not a query']",
    "[a <urn:UnknownRule>; sh:unknown true]",
    "[a sh:TripleRule; sh:condition [sh:nodeKind <urn:UnknownKind>]]",
    "[a sh:TripleRule; sh:object [sh:filterShape [sh:nodeKind <urn:UnknownKind>]]]",
    '[a sh:TripleRule; sh:object [sh:path "not a path"]]',
]


@pytest.mark.parametrize("rule", RULES)
@pytest.mark.parametrize("has_required", [False, True])
def test_disabled_rules_match_original_core_validation(rule, has_required):
    results = []
    for module in ("pyshacl", "pyshacl_turbo"):
        data = Graph().parse(data="<urn:focus> <urn:p> true.", format="turtle")
        if has_required:
            data.add((URIRef("urn:focus"), URIRef("urn:required"), URIRef("urn:value")))
        original = set(data)
        shapes = Graph().parse(
            data=PREFIX
            + "<urn:S> sh:targetNode <urn:focus>; sh:property [sh:path <urn:required>; "
            + "sh:minCount 1]; sh:rule "
            + rule
            + ".",
            format="turtle",
        )
        result = importlib.import_module(module).validate(
            data, shacl_graph=shapes, advanced=False, inplace=True
        )
        assert result[0] is has_required
        assert set(data) == original
        results.append(result)
    assert isomorphic(results[0][1], results[1][1])
    assert results[0][2] == results[1][2]


@pytest.mark.parametrize("module", ["pyshacl", "pyshacl_turbo"])
def test_enabled_valid_rule_still_executes(module):
    data = Graph()
    shapes = Graph().parse(
        data=PREFIX + "<urn:S> sh:targetNode <urn:focus>; sh:rule " + RULES[0] + ".",
        format="turtle",
    )
    assert importlib.import_module(module).validate(
        data, shacl_graph=shapes, advanced=True, inplace=True
    )[0]
    assert list(data.objects(URIRef("urn:focus"), URIRef("urn:added")))


@pytest.mark.parametrize(
    "annotation",
    [
        "sh:target [a <urn:UnknownTarget>]",
        "sh:expression [sh:unknown true]",
    ],
)
def test_disabled_advanced_annotations_do_not_change_core_validation(annotation):
    reports = []
    for module in ("pyshacl", "pyshacl_turbo"):
        shapes = Graph().parse(
            data=PREFIX
            + "<urn:S> sh:targetNode <urn:focus>; sh:property [sh:path <urn:p>; "
            + "sh:minCount 1]; "
            + annotation
            + ".",
            format="turtle",
        )
        reports.append(
            importlib.import_module(module).validate(Graph(), shacl_graph=shapes, advanced=False)
        )
    assert reports[0][0] is reports[1][0] is False
    assert isomorphic(reports[0][1], reports[1][1])
    assert reports[0][2] == reports[1][2]


@pytest.mark.parametrize("advanced", [False, True])
def test_non_shape_path_annotations_are_not_executable_paths(advanced):
    for module in ("pyshacl", "pyshacl_turbo"):
        shapes = Graph().parse(
            data=PREFIX
            + '<urn:metadata> sh:path "not a path". '
            + "<urn:S> sh:targetNode <urn:focus>; sh:class <urn:Required>.",
            format="turtle",
        )
        assert (
            importlib.import_module(module).validate(
                Graph(), shacl_graph=shapes, advanced=advanced
            )[0]
            is False
        )


@pytest.mark.parametrize("module", ["pyshacl", "pyshacl_turbo"])
@pytest.mark.parametrize(
    "declaration",
    [
        "sh:target [a sh:SPARQLTarget; sh:select "
        + "'SELECT ?this WHERE {VALUES ?this {<urn:focus>}}']; sh:class <urn:Required>",
        "sh:targetNode <urn:focus>; sh:expression false",
    ],
)
def test_enabled_advanced_annotations_still_execute(module, declaration):
    shapes = Graph().parse(
        data=PREFIX + "<urn:S> a sh:NodeShape; " + declaration + ".", format="turtle"
    )
    assert (
        importlib.import_module(module).validate(Graph(), shacl_graph=shapes, advanced=True)[0]
        is False
    )


@pytest.mark.parametrize("module", ["pyshacl", "pyshacl_turbo"])
def test_advanced_target_alone_does_not_register_a_shape(module):
    shapes = Graph().parse(
        data=PREFIX
        + "<urn:metadata> sh:target [a sh:SPARQLTarget; sh:select "
        + "'SELECT ?this WHERE {VALUES ?this {<urn:focus>}}']; sh:class <urn:Required>.",
        format="turtle",
    )
    assert (
        importlib.import_module(module).validate(Graph(), shacl_graph=shapes, advanced=True)[0]
        is True
    )
