"""Public runner contracts execute the native engine and match pySHACL0.40.1."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from pyshacl.graph_abstraction import DataGraph as ReferenceDataGraph
from rdflib import BNode, Dataset, Graph, Literal
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, SH
from test_datagraph_contract import EX, fixture, wrapped


def test_public_runner_classes_are_independent_reference_types():
    for engine, module in ((pyshacl, "pyshacl"), (turbo, "pyshacl_turbo")):
        data, shapes = fixture()
        runner = engine.RuleExpandRunner(wrapped(module, data), shacl_graph=shapes)
        assert not isinstance(runner, engine.Validator)


def test_rule_runner_uses_its_executor_depth_policy():
    for engine, module in ((pyshacl, "pyshacl"), (turbo, "pyshacl_turbo")):
        data, shapes = fixture()
        shapes = Graph()
        shapes.add((EX.S, SH.targetNode, EX.a))
        shapes.add((EX.S, SH.rule, EX.rule))
        for predicate, value in (
            (RDF.type, SH.TripleRule),
            (SH.subject, SH.this),
            (SH.predicate, EX.flag),
            (SH.object, Literal(True)),
            (SH.condition, EX.Condition0),
        ):
            shapes.add((EX.rule, predicate, value))
        for index in range(8):
            shapes.add((EX[f"Condition{index}"], SH.node, EX[f"Condition{index + 1}"]))
        shapes.add((EX.Condition8, SH["class"], EX.Person))
        runner = engine.RuleExpandRunner(
            wrapped(module, data), shacl_graph=shapes, options={"max_validation_depth": 1}
        )
        assert runner.make_executor().max_validation_depth == 999
        assert (EX.a, EX.flag, Literal(True)) in runner.run()


@pytest.mark.parametrize("conforms", [False, True])
def test_public_report_builder_preserves_result_terms_closure_and_sorted_text(conforms):
    source = Graph()
    node, child = BNode("source-shape"), BNode("child")
    source.add((node, EX.link, child))
    source.add((child, EX.link, node))
    source.add((child, EX.label, Literal("01", normalize=False)))
    result = BNode("result")
    results = [
        ("Z result\n", result, [(result, SH.sourceShape, (source, node))]),
        (
            "A result\n",
            BNode("other-result"),
            [
                (result, SH.value, (source, Literal("value"))),
                (result, SH.focusNode, (source, EX.a)),
                (result, SH.sourceShape, (source, node)),
            ],
        ),
    ]
    reports = []
    for engine in (pyshacl, turbo):
        shapes = engine.ShapesGraph(Graph())
        report, text = engine.Validator.create_validation_report(shapes, conforms, results)
        assert (node, EX.link, None) in report
        assert (None, EX.label, Literal("01", normalize=False)) in report
        assert text.endswith("A result\nZ result\n")
        reports.append((report, text))
    assert isomorphic(reports[0][0], reports[1][0])
    assert reports[0][1] == reports[1][1]


def test_public_report_builder_requires_results_for_nonconformance():
    for engine in (pyshacl, turbo):
        shapes = engine.ShapesGraph(Graph())
        with pytest.raises(RuntimeError, match="at least one result"):
            engine.Validator.create_validation_report(shapes, False, [])
        graph, text = engine.Validator.create_validation_report(shapes, True, [])
        assert len(graph) == 2 and text == "Validation Report\nConforms: True\n"


@pytest.mark.parametrize("runner_name", ["Validator", "RuleExpandRunner"])
@pytest.mark.parametrize("dataset", [False, True])
@pytest.mark.parametrize("inplace", [False, True])
def test_public_ontology_mixing_preserves_reference_scope_and_identity(
    runner_name, dataset, inplace
):
    from rdflib.namespace import RDFS

    outputs = []
    for engine, module in ((pyshacl, "pyshacl"), (turbo, "pyshacl_turbo")):
        data, shapes = fixture(dataset)
        source = wrapped(module, data)
        before = set(source)
        ontology = Graph()
        ontology.add((EX.Child, RDFS.subClassOf, EX.Parent))
        runner = getattr(engine, runner_name)(
            source, shacl_graph=shapes, ont_graph=ontology, options={"inplace": inplace}
        )
        result = runner.mix_in_ontology()
        assert isinstance(result, type(source))
        assert (result is source) is inplace
        assert runner.target_graph is None
        assert not runner.pre_inferenced
        assert (EX.Child, RDFS.subClassOf, EX.Parent) in result
        if not inplace:
            assert set(source) == before
        outputs.append(set(result))
    assert outputs[0] == outputs[1]


@pytest.mark.parametrize("runner_name", ["Validator", "RuleExpandRunner"])
def test_runner_executor_options_match_reference(runner_name):
    executors = []
    for engine, module in ((pyshacl, "pyshacl"), (turbo, "pyshacl_turbo")):
        data, shapes = fixture()
        runner = getattr(engine, runner_name)(
            wrapped(module, data),
            shacl_graph=shapes,
            options={
                "advanced": True,
                "abort_on_first": True,
                "allow_infos": True,
                "allow_warnings": True,
                "iterate_rules": True,
                "max_validation_depth": 4,
                "focus_nodes": [EX.a],
            },
        )
        executor = runner.make_executor()
        assert executor.validator is runner
        executors.append(
            {name: value for name, value in vars(executor).items() if name != "validator"}
        )
    assert executors[0] == executors[1]


def test_direct_validator_raises_validation_failure_instead_of_top_level_result():
    shapes = Graph().parse(
        data="""@prefix sh: <http://www.w3.org/ns/shacl#> .
        <urn:S> sh:targetNode <urn:s>; sh:sparql [sh:select
          "SELECT $this WHERE { VALUES ?v {1} }"].""",
        format="turtle",
    )
    for engine, module, failure in (
        (pyshacl, "pyshacl", pyshacl.errors.ValidationFailure),
        (turbo, "pyshacl_turbo", turbo.ValidationFailure),
    ):
        runner = engine.Validator(wrapped(module, Graph()), shacl_graph=shapes)
        with pytest.raises(failure, match="VALUES"):
            runner.run()


@pytest.mark.parametrize("dataset", [False, True])
@pytest.mark.parametrize("inplace", [False, True])
def test_validator_constructor_and_run_match_reference(dataset, inplace):
    expected_data, expected_shapes = fixture(dataset)
    actual_data, actual_shapes = fixture(dataset)
    expected = pyshacl.Validator(
        ReferenceDataGraph.from_rdflib(expected_data),
        shacl_graph=expected_shapes,
        options={"inplace": inplace},
    )
    actual = turbo.Validator(
        wrapped("pyshacl_turbo", actual_data),
        shacl_graph=actual_shapes,
        options={"inplace": inplace},
    )
    assert actual.target_graph is expected.target_graph is None
    assert actual.data_graph.impl is actual_data
    assert actual.shacl_graph.graph is actual_shapes
    assert actual.options.keys() == expected.options.keys()
    expected_result, actual_result = (expected.run(), actual.run())
    assert actual_result[0] == expected_result[0] is False
    assert isomorphic(actual_result[1], expected_result[1])
    assert actual_result[2] == expected_result[2]
    assert set(actual.target_graph) == set(expected.target_graph)
    assert actual.data_graph_is_multigraph == expected.data_graph_is_multigraph
    assert actual.inplace == expected.inplace
    assert actual.pre_inferenced == expected.pre_inferenced


def test_validator_rejects_raw_graph_and_unknown_execution_options_fail_fast():
    graph, shapes = fixture()
    for cls in (pyshacl.Validator, turbo.Validator):
        with pytest.raises(RuntimeError, match="data_graph must be a DataGraph object"):
            cls(graph, shacl_graph=shapes)
    with pytest.raises(NotImplementedError, match="SHACL-JS"):
        turbo.Validator(
            wrapped("pyshacl_turbo", graph), shacl_graph=shapes, options={"use_js": True}
        ).run()


def test_rule_runner_no_argument_run_matches_reference():
    expected_data, expected_shapes = fixture()
    actual_data, actual_shapes = fixture()
    expected = pyshacl.RuleExpandRunner(
        ReferenceDataGraph.from_rdflib(expected_data), shacl_graph=expected_shapes
    )
    actual = turbo.RuleExpandRunner(
        wrapped("pyshacl_turbo", actual_data), shacl_graph=actual_shapes
    )
    assert actual.options.keys() == expected.options.keys()
    assert set(actual.run()) == set(expected.run())
    assert actual.target_graph is not None


@pytest.mark.parametrize("runner_name", ["Validator", "RuleExpandRunner"])
@pytest.mark.parametrize("inplace", [False, True])
def test_runner_inference_prepared_once_and_options_are_not_ignored(runner_name, inplace):
    from rdflib.namespace import RDFS

    runners = []
    for engine, module in ((pyshacl, "pyshacl"), (turbo, "pyshacl_turbo")):
        data = Graph(identifier=EX.data)
        data.add((EX.a, RDF.type, EX.Child))
        data.add((EX.Child, RDFS.subClassOf, EX.Parent))
        shape = Graph()
        shape.add((EX.S, RDF.type, SH.NodeShape))
        shape.add((EX.S, SH.targetClass, EX.Parent))
        runner = getattr(engine, runner_name)(
            wrapped(module, data),
            shacl_graph=shape,
            options={"inference": "rdfs", "inplace": inplace},
        )
        assert not runner.pre_inferenced
        runner.run()
        assert runner.pre_inferenced
        assert (EX.a, RDF.type, EX.Parent) in runner.target_graph
        assert ((EX.a, RDF.type, EX.Parent) in data) == inplace
        target = runner.target_graph
        runner.run()
        assert runner.target_graph is target
        runners.append(runner)
    assert set(runners[0].target_graph) == set(runners[1].target_graph)


def test_runner_default_shapes_snapshot_and_preinferenced_flag():
    for engine, module in ((pyshacl, "pyshacl"), (turbo, "pyshacl_turbo")):
        data = Graph()
        data.add((EX.S, RDF.type, SH.NodeShape))
        runner = engine.Validator(
            wrapped(module, data),
            pre_inferenced=True,
            options={"inference": "rdfs", "advanced": True},
        )
        data.add((EX.Later, RDF.type, SH.NodeShape))
        assert (EX.Later, RDF.type, SH.NodeShape) not in runner.shacl_graph.graph
        assert runner.run()[0] is True
        assert runner.target_graph.impl is not data


def test_runner_logger_remote_options_and_ontology_are_explicit():
    import logging

    from rdflib.namespace import RDFS

    data, shapes = fixture()
    logger = logging.getLogger("parity-constructor")
    explicit = turbo.Validator(
        wrapped("pyshacl_turbo", data), shacl_graph=shapes, options={"logger": logger}
    )
    assert explicit.logger is logger
    debug = turbo.Validator(
        wrapped("pyshacl_turbo", data), shacl_graph=shapes, options={"debug": True}
    )
    assert debug.logger.getEffectiveLevel() == logging.DEBUG
    with pytest.raises(NotImplementedError, match="Remote SPARQL"):
        turbo.Validator(
            wrapped("pyshacl_turbo", data), shacl_graph=shapes, options={"sparql_mode": True}
        ).run()
    ontology = Dataset()
    ontology.default_graph.add((EX.Child, RDFS.subClassOf, EX.Parent))
    runner = turbo.Validator(wrapped("pyshacl_turbo", data), shacl_graph=shapes, ont_graph=ontology)
    assert ontology.default_union
    runner.run()
    assert runner.target_graph is not runner.data_graph


def test_rule_runner_always_runs_rules_even_if_advanced_option_is_false():
    outputs = []
    for engine, module in ((pyshacl, "pyshacl"), (turbo, "pyshacl_turbo")):
        data, shapes = fixture()
        rule = BNode("always-active-rule")
        shapes.add((EX.S, SH.rule, rule))
        for predicate, value in (
            (RDF.type, SH.TripleRule),
            (SH.subject, SH.this),
            (SH.predicate, EX.flag),
            (SH.object, Literal(True)),
        ):
            shapes.add((rule, predicate, value))
        result = engine.RuleExpandRunner(
            wrapped(module, data), shacl_graph=shapes, options={"advanced": False}
        ).run()
        assert (EX.a, EX.flag, Literal(True)) in result
        outputs.append(set(result.triples((None, None, None))))
    assert outputs[0] == outputs[1]
