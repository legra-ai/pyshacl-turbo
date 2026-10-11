import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.namespace import RDF, SH, XSD
from test_compatibility import EX, PREFIXES, graph


def test_turtle_text_is_detected_without_an_explicit_format():
    assert turbo.validate(PREFIXES + 'ex:s ex:p "ok".', shacl_graph=PREFIXES)[0]


def test_file_uri_and_bytes_loading_preserve_literal_terms(tmp_path):
    path = tmp_path / "data.ttl"
    path.write_text(PREFIXES + 'ex:s ex:p "01"^^xsd:integer.')
    loaded = turbo.load_from_source(path.as_uri())
    assert loaded.value(EX.s, EX.p) == Literal("01", datatype=XSD.integer, normalize=False)
    assert len(turbo.load_from_source(path.read_bytes())) == 1


def test_loader_resolves_relative_imports_once_and_handles_cycles(tmp_path):
    a, b = tmp_path / "a.ttl", tmp_path / "b.ttl"
    owl = "@prefix owl: <http://www.w3.org/2002/07/owl#>. "
    a.write_text(owl + "<> a owl:Ontology; owl:imports <b.ttl>.")
    b.write_text(owl + "<> a owl:Ontology; owl:imports <a.ttl>.")
    loaded = turbo.load_from_source(a, do_owl_imports=True)
    assert len(loaded) == 4


def test_dataset_validation_uses_union_without_mutating_input():
    data = Dataset()
    data.graph(EX.g1).add((EX.s, EX.p, Literal("one")))
    data.graph(EX.g2).add((EX.s, EX.p, Literal("two")))
    before = set(data.quads())
    conforms, report, _ = turbo.validate(
        data, shacl_graph=graph("ex:S sh:targetNode ex:s; sh:path ex:p; sh:maxCount 1.")
    )
    assert not conforms
    assert list(report.objects(None, SH.focusNode)) == [EX.s]
    assert set(data.quads()) == before


def test_multiple_inputs_combine_and_validate_each():
    shapes = graph("ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1; sh:maxCount 1.")
    data = [graph("ex:s ex:p 1."), graph("ex:s ex:p 2.")]
    assert not turbo.validate(data, shacl_graph=shapes)[0]
    assert [r[0] for r in turbo.validate_each(data, shacl_graph=shapes).values()] == [True, True]


def test_empty_multiple_input_fails():
    with pytest.raises(RuntimeError, match="No data graphs"):
        turbo.validate([])


def test_ontology_rdfs_domain_and_subproperty_are_inferred_natively():
    data = graph('ex:s ex:child "value".')
    ont = graph("ex:child rdfs:subPropertyOf ex:p. ex:p rdfs:domain ex:Person.")
    shapes = graph("ex:S sh:targetClass ex:Person; sh:path ex:q; sh:minCount 1.")
    conforms, report, _ = turbo.validate(data, shacl_graph=shapes, ont_graph=ont, inference="rdfs")
    assert not conforms
    assert list(report.objects(None, SH.focusNode)) == [EX.s]
    assert len(data) == 1


def test_warning_and_info_options_preserve_results():
    shapes = graph("ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1; sh:severity sh:Warning.")
    assert not turbo.validate(graph(""), shacl_graph=shapes, allow_infos=True)[0]
    conforms, report, _ = turbo.validate(graph(""), shacl_graph=shapes, allow_warnings=True)
    assert conforms
    assert len(list(report.objects(None, SH.result))) == 1
    assert report.value(None, SH.conforms, Literal(True)) is not None


def test_focus_and_shape_selection_can_bypass_declared_targets():
    shapes = graph("ex:S sh:targetNode ex:a; sh:path ex:p; sh:minCount 1.")
    _, report, _ = turbo.validate(
        graph(""), shacl_graph=shapes, focus_nodes=[str(EX.b)], use_shapes=[str(EX.S)]
    )
    assert list(report.objects(None, SH.focusNode)) == [EX.b]
    assert turbo.validate(graph(""), shacl_graph=shapes, focus_nodes=[str(EX.b)])[0]


def test_report_serialization_and_debug_option():
    result = turbo.validate(
        graph(""), shacl_graph=graph(""), debug=True, serialize_report_graph="turtle"
    )
    assert isinstance(result[1], bytes)
    assert len(Graph().parse(data=result[1], format="turtle")) == 2


def test_report_retains_shapes_namespace_bindings():
    _, report, _ = turbo.validate(
        graph(""), shacl_graph=graph("ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1.")
    )
    assert dict(report.namespaces())["ex"] == URIRef(EX)


def test_closed_constraint_matches_reference_resource_exception():
    from test_compatibility import compare

    compare(graph("ex:s a rdfs:Resource."), graph("ex:S sh:targetNode ex:s; sh:closed true."))


def test_shapes_file_boolean_policy_differs_from_graph_input(tmp_path):
    import pyshacl

    text = PREFIXES + 'ex:S sh:targetNode ex:s; sh:path ex:p; sh:uniqueLang "1"^^xsd:boolean.'
    path = tmp_path / "shapes.ttl"
    path.write_text(text)
    data = graph('ex:s ex:p "one"@en, "two"@en.')
    for shapes in [str(path), Graph().parse(data=text, format="turtle")]:
        assert (
            turbo.validate(data, shacl_graph=shapes)[0]
            == pyshacl.validate(data, shacl_graph=shapes)[0]
        )


def test_validation_failure_public_result_and_strict_compiler():
    shapes = graph(
        'ex:S sh:targetNode ex:s; sh:sparql [sh:select "SELECT $this WHERE { VALUES ?v {1} }"].'
    )
    conforms, failure, text = turbo.validate(graph(""), shacl_graph=shapes)
    assert not conforms
    assert isinstance(failure, turbo.ValidationFailure)
    assert "VALUES" in failure.message
    assert "Validation Failure" in text
    with pytest.raises(turbo.ValidationFailure):
        turbo.compile_shapes(shapes)


def test_implicit_owl_class_target_matches_reference():
    from test_compatibility import compare

    compare(
        graph("ex:s a ex:Person."),
        graph("""
      ex:Person a <http://www.w3.org/2002/07/owl#Class>, sh:NodeShape;
        sh:property [sh:path ex:p; sh:minCount 1; sh:message "missing"].
    """),
    )


def test_sparql_uses_graph_namespace_bindings():
    from test_compatibility import compare

    compare(
        graph("ex:s ex:p 1."),
        graph("""
      ex:S sh:targetNode ex:s; sh:sparql [sh:message "bad";
        sh:select "SELECT $this WHERE { $this ex:p ?v }"].
    """),
    )


def test_focus_curie_comes_from_data_namespace_after_inference():
    data = graph("ex:s a ex:Person.")
    data.bind("focus", EX)
    shapes = graph("ex:S sh:targetClass ex:Person; sh:path ex:p; sh:minCount 1.")
    conforms, report, _ = turbo.validate(
        data, shacl_graph=shapes, focus_nodes=["focus:s"], inference="rdfs"
    )
    assert not conforms
    assert list(report.objects(None, SH.focusNode)) == [EX.s]


def test_meta_shacl_validates_shapes_before_data():
    valid = graph("ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1.")
    assert turbo.meta_validate(valid)[0]
    invalid = graph("ex:S a sh:PropertyShape; sh:path 42.")
    assert not turbo.meta_validate(invalid)[0]
    with pytest.raises(RuntimeError, match="MetaSHACL"):
        turbo.validate(graph(""), shacl_graph=invalid, meta_shacl=True)


def test_dash_compares_the_report_instead_of_its_conformance_flag():
    dash = "@prefix dash: <http://datashapes.org/dash#>. "
    shapes = (
        PREFIXES
        + dash
        + """
      ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1.
      ex:test a dash:GraphValidationTestCase; dash:expectedResult [
        a sh:ValidationReport; sh:conforms false; sh:result [
          a sh:ValidationResult; sh:focusNode ex:s; sh:resultPath ex:p;
          sh:sourceShape ex:S; sh:resultSeverity sh:Violation;
          sh:sourceConstraintComponent sh:MinCountConstraintComponent]].
    """
    )
    assert turbo.validate(shapes, check_dash_result=True)[0]
    assert not turbo.validate(
        shapes.replace("sh:focusNode ex:s", "sh:focusNode ex:wrong"), check_dash_result=True
    )[0]


def test_relative_file_iri_is_a_document(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data.ttl").write_text("<urn:s> <urn:p> 1.")
    result = turbo.load_from_source("file:./data.ttl")
    assert len(result) == 1


@pytest.mark.parametrize("named", [False, True])
@pytest.mark.parametrize("validate", [pyshacl.validate, turbo.validate])
def test_dataset_inplace_preparation_preserves_inference_destination(named, validate):
    from rdflib import Dataset

    data = Dataset(default_union=True)
    (data.graph(EX.g) if named else data.default_graph).parse(
        data=PREFIXES + "ex:s a ex:A.", format="turtle"
    )
    ontology = graph("ex:A rdfs:subClassOf ex:B.")
    validate(
        data,
        shacl_graph=graph("ex:S sh:targetClass ex:B; sh:class ex:B."),
        ont_graph=ontology,
        inference="rdfs",
        inplace=True,
    )
    assert (EX.s, RDF.type, EX.A) in (data.graph(EX.g) if named else data.default_graph)
    assert (EX.s, RDF.type, EX.B) in data.graph(URIRef("urn:pyshacl:inference"))
    assert (EX.s, RDF.type, EX.B) not in data.default_graph


def test_ignored_properties_without_closed_is_invalid():
    with pytest.raises(ValueError, match="ignoredProperties"):
        turbo.validate(
            graph(""), shacl_graph=graph("ex:S a sh:NodeShape; sh:ignoredProperties (ex:type).")
        )


def test_function_declarations_are_inactive_without_advanced_mode():
    shapes = graph("""ex:fn a sh:NamedParameterExpressionFunction;
      sh:expression [sh:path ex:p]; sh:returnType xsd:string.
      ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1.""")
    assert not turbo.validate(graph(""), shacl_graph=shapes)[0]


@pytest.mark.parametrize("typed", [False, True])
def test_parameter_annotations_do_not_create_executable_shapes(typed):
    shapes = graph("""ex:C a sh:ConstraintComponent;
      sh:parameter [sh:path ex:annotation].
      ex:Function sh:parameter ex:P.
      ex:P sh:path ex:p; sh:node ex:ValueShape; ex:annotation ex:Value.
      ex:ValueShape a sh:NodeShape; sh:class ex:Value.
      ex:S a sh:NodeShape; sh:targetNode ex:s; sh:class ex:Required.""")
    if typed:
        shapes.add((EX.P, RDF.type, SH.Parameter))
    assert not turbo.validate(graph(""), shacl_graph=shapes)[0]


def test_targeted_shape_still_rejects_component_without_validator():
    shapes = graph("""ex:C a sh:ConstraintComponent;
      sh:parameter [sh:path ex:annotation].
      ex:S sh:targetNode ex:s; ex:annotation ex:Value.""")
    with pytest.raises(NotImplementedError, match="No applicable validator"):
        turbo.validate(graph(""), shacl_graph=shapes)


@pytest.mark.parametrize(
    "role", ["ex:P sh:targetNode ex:s.", "ex:S sh:targetNode ex:s; sh:node ex:P."]
)
def test_parameter_used_as_shape_still_requires_a_validator(role):
    shapes = graph(
        """ex:C a sh:ConstraintComponent;
      sh:parameter [sh:path ex:annotation].
      ex:Function sh:parameter ex:P.
      ex:P a sh:Parameter; sh:path ex:p; ex:annotation ex:Value.
    """
        + role
    )
    with pytest.raises(NotImplementedError, match="No applicable validator"):
        turbo.validate(graph(""), shacl_graph=shapes)


def test_imported_core_component_declaration_uses_native_implementation():
    shapes = graph("""sh:MinCountConstraintComponent a sh:ConstraintComponent;
      sh:parameter [sh:path sh:minCount].
      sh:PropertyConstraintComponent a sh:ConstraintComponent;
        sh:parameter [sh:path sh:property].
      ex:S sh:targetNode ex:s; sh:property [sh:path ex:p; sh:minCount 1].""")
    conforms, report, _ = turbo.validate(graph(""), shacl_graph=shapes)
    assert not conforms
    assert list(report.objects(None, SH.sourceConstraintComponent)) == [
        SH.MinCountConstraintComponent
    ]
