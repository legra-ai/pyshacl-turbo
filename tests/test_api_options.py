"""Exercise option validation and graph preparation through the public APIs."""

import pyoxigraph as ox
import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Literal
from rdflib.namespace import RDF, RDFS, SH
from test_compatibility import EX, PREFIXES, graph


@pytest.mark.parametrize("method", ["validate", "shacl_rules"])
def test_compiled_inplace_requires_a_mutable_graph_or_store(method):
    program = turbo.compile_shapes(graph(""))
    with pytest.raises(TypeError, match="inplace=True requires"):
        getattr(program, method)(PREFIXES, inplace=True)


@pytest.mark.parametrize(
    "options", [{"inference": "rdfs"}, {"ont_graph": Graph()}, {"inplace": True}]
)
def test_sparql_mode_rejects_local_graph_mutation_and_preinference(options):
    with pytest.raises(turbo.ReportableRuntimeError, match="SPARQL Remote Graph Mode") as error:
        turbo.validate(graph(""), sparql_mode=True, **options)
    assert error.value.message == str(error.value)


def test_remote_sparql_endpoint_is_explicitly_unsupported():
    with pytest.raises(NotImplementedError, match="Remote SPARQL endpoint"):
        turbo.validate("https://example.invalid/sparql", sparql_mode=True)


@pytest.mark.parametrize("data", [graph(""), PREFIXES])
def test_sparql_mode_can_query_local_inputs(data):
    assert turbo.validate(data, shacl_graph=graph(""), sparql_mode=True)[0]


def test_validate_each_option_returns_independent_results_and_preserves_options():
    shapes = graph("ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1; sh:severity sh:Warning.")
    results = turbo.validate(
        [graph(""), graph("ex:s ex:p 1.")],
        shacl_graph=shapes,
        multi_data_graphs_mode="validate_each",
        allow_warnings=True,
    )
    assert list(results) == [0, 1]
    assert [result[0] for result in results.values()] == [True, True]
    assert [len(list(result[1].objects(None, SH.result))) for result in results.values()] == [1, 0]


def test_invalid_multi_graph_modes_and_empty_validate_each_are_errors():
    with pytest.raises(turbo.ReportableRuntimeError, match="Unknown multi_data_graphs_mode"):
        turbo.validate([graph("")], multi_data_graphs_mode="invalid")
    with pytest.raises(RuntimeError, match="No data graphs"):
        turbo.validate_each([])


@pytest.mark.parametrize("option", ["meta_shacl", "metashacl"])
def test_valid_meta_shapes_do_not_prevent_data_validation(option):
    shapes = graph("ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1.")
    assert turbo.validate(graph("ex:s ex:p 1."), shacl_graph=shapes, **{option: True})[0]


@pytest.mark.parametrize("option", ["meta_shacl", "metashacl", "check_dash_result"])
def test_rule_runner_rejects_validation_only_options(option):
    with pytest.raises(NotImplementedError, match=f"Unsupported option: {option}"):
        turbo.shacl_rules(graph(""), **{option: True})


@pytest.mark.parametrize("rules", [False, True])
def test_imported_shapes_participate_in_validation_and_rules(tmp_path, rules):
    root, imported = tmp_path / "root.ttl", tmp_path / "imported.ttl"
    root.write_text(
        PREFIXES + f"<urn:ontology> <http://www.w3.org/2002/07/owl#imports> <{imported.as_uri()}>."
    )
    imported.write_text(
        PREFIXES
        + "ex:S sh:targetNode ex:s; sh:path ex:required; sh:minCount 1; sh:rule [a sh:TripleRule; sh:subject sh:this; sh:predicate ex:derived; sh:object 2]."
    )
    data = graph("")
    if rules:
        result = turbo.shacl_rules(data, shacl_graph=root, do_owl_imports=True)
        assert (EX.s, EX.derived, Literal(2)) in result
    else:
        conforms, report, _ = turbo.validate(
            data, shacl_graph=root, do_owl_imports=True, advanced=True
        )
        assert not conforms
        assert list(report.objects(None, SH.resultPath)) == [EX.required]


def test_rule_runner_uses_embedded_shapes_when_none_are_supplied():
    source = graph(
        "ex:S sh:targetNode ex:s; sh:rule [a sh:TripleRule; sh:subject sh:this; sh:predicate ex:p; sh:object 2]."
    )
    result = turbo.shacl_rules(source, max_validation_depth=None)
    assert (EX.s, EX.p, Literal(2)) in result
    assert (EX.s, EX.p, None) not in source


@pytest.mark.parametrize("store", [False, True])
def test_rule_inference_commits_to_the_original_input(store):
    data = graph("ex:s a ex:Child. ex:Child rdfs:subClassOf ex:Parent.")
    if store:
        target = ox.Store()
        target.load(input=data.serialize(format="nt"), format=ox.RdfFormat.N_TRIPLES)
        data = target
    shapes = graph(
        "ex:S sh:targetClass ex:Parent; sh:rule [a sh:TripleRule; sh:subject sh:this; sh:predicate ex:p; sh:object 2]."
    )
    result = turbo.shacl_rules(data, shacl_graph=shapes, inference="rdfs", inplace=True)
    assert (EX.s, EX.p, Literal(2)) in turbo.load_from_source(data)
    if not store:
        assert result is data


def test_inference_accepts_namespace_free_graphs_and_shape_focus_prefixes():
    data = Graph(bind_namespaces="none")
    data.add((EX.s, RDF.type, EX.Child))
    data.add((EX.Child, RDFS.subClassOf, EX.Parent))
    shapes = graph("ex:S sh:targetClass ex:Parent; sh:class ex:Parent.")
    assert turbo.validate(data, shacl_graph=shapes, inference="rdfs", focus_nodes=["ex:s"])[0]


def test_ontology_inoculation_without_inference_preserves_original_types():
    data = graph("ex:s a ex:Child.")
    ontology = graph("ex:Parent a rdfs:Class. ex:Child rdfs:subClassOf ex:Parent.")
    shapes = graph("ex:S sh:targetNode ex:s; sh:class ex:Parent.")
    assert turbo.validate(
        data, shacl_graph=shapes, ont_graph=ontology, inference="none", inplace=True
    )[0]
    assert (EX.Child, RDFS.subClassOf, EX.Parent) in data
    assert (EX.s, RDF.type, EX.Parent) not in data
