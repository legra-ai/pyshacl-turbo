"""Report text uses pinned pySHACL literal descriptions, never RDF serialization."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
import rdflib
from rdflib import BNode, Graph, Literal, Namespace
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, SH, XSD

EX = Namespace("urn:example:")
ERROR = Namespace("http://www.daml.org/2002/03/agents/agent-ont#")
LITERALS = [
    Literal("plain"),
    Literal('say "hi"\\end'),
    Literal("line\nnext\tcol\rreturn"),
    Literal("français", lang="fr"),
    Literal("same", datatype=XSD.string),
    Literal("1", datatype=XSD.integer),
    Literal("+001", datatype=XSD.integer, normalize=False),
    Literal("true", datatype=XSD.boolean),
    Literal("1", datatype=XSD.boolean, normalize=False),
    Literal("01.20", datatype=XSD.decimal, normalize=False),
    Literal("opaque", datatype=EX.opaque),
]


@pytest.mark.parametrize("literal", LITERALS)
@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("normalize", [False, True])
def test_complete_report_preserves_literal_descriptions(monkeypatch, literal, nested, normalize):
    monkeypatch.setattr(rdflib, "NORMALIZE_LITERALS", normalize)
    data = Graph()
    data.bind("ex", EX)
    shapes = Graph()
    shapes.bind("ex", EX)
    property_shape = BNode()
    shapes.add((EX.Shape, SH.targetNode, EX.s))
    shapes.add((EX.Shape, SH.property, property_shape))
    shapes.add((property_shape, SH.path, EX.required))
    shapes.add((property_shape, SH.minCount, Literal(1)))
    if nested:
        note = BNode()
        shapes.add((property_shape, EX.note, note))
        shapes.add((note, EX.value, literal))
    else:
        shapes.add((property_shape, EX.note, literal))
    expected = pyshacl.validate(data, shacl_graph=shapes)
    assert rdflib.NORMALIZE_LITERALS is True
    monkeypatch.setattr(rdflib, "NORMALIZE_LITERALS", normalize)
    original_data, original_shapes = set(data), set(shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert actual[0] == expected[0] == False
    assert actual[2] == expected[2]
    assert isomorphic(actual[1], expected[1])
    assert set(data) == original_data
    assert set(shapes) == original_shapes
    assert rdflib.NORMALIZE_LITERALS is normalize


@pytest.mark.parametrize("normalize", [False, True])
def test_complete_report_describes_inference_error_literal_without_reescaping(
    monkeypatch, normalize
):
    monkeypatch.setattr(rdflib, "NORMALIZE_LITERALS", normalize)
    data = Graph()
    data.bind("err", ERROR)
    error = BNode()
    data.add((error, RDF.type, ERROR.ErrorMessage))
    data.add(
        (
            error,
            ERROR.error,
            Literal(
                "Lexical value of the literal 'bad' does not match its datatype "
                "(http://www.w3.org/2001/XMLSchema#integer)"
            ),
        )
    )
    shapes = Graph().parse(
        data="""@prefix sh:<http://www.w3.org/ns/shacl#>.
        <urn:S> sh:targetClass
        <http://www.daml.org/2002/03/agents/agent-ont#ErrorMessage>;
        sh:property [sh:path <urn:required>;sh:minCount 1].""",
        format="turtle",
    )
    expected = pyshacl.validate(data, shacl_graph=shapes)
    assert rdflib.NORMALIZE_LITERALS is True
    monkeypatch.setattr(rdflib, "NORMALIZE_LITERALS", normalize)
    original_data, original_shapes = set(data), set(shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert actual[0] == expected[0] == False
    assert actual[2] == expected[2]
    assert isomorphic(actual[1], expected[1])
    assert set(data) == original_data
    assert set(shapes) == original_shapes
    assert rdflib.NORMALIZE_LITERALS is normalize


@pytest.mark.parametrize("normalize", [False, True])
def test_direct_report_value_keeps_its_original_lexical_term(monkeypatch, normalize):
    monkeypatch.setattr(rdflib, "NORMALIZE_LITERALS", normalize)
    value = Literal("+001", datatype=XSD.integer, normalize=False)
    data = Graph()
    data.bind("ex", EX)
    data.add((EX.s, EX.p, value))
    shapes = Graph().parse(
        data="""@prefix ex:<urn:example:>. @prefix sh:<http://www.w3.org/ns/shacl#>.
        @prefix xsd:<http://www.w3.org/2001/XMLSchema#>.
        ex:S sh:targetNode ex:s; sh:property [sh:path ex:p;sh:pattern "^absent$"].""",
        format="turtle",
    )
    expected = pyshacl.validate(data, shacl_graph=shapes)
    monkeypatch.setattr(rdflib, "NORMALIZE_LITERALS", normalize)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert set(actual[1].objects(None, SH.value)) == {value}
    assert actual[2] == expected[2]
    assert isomorphic(actual[1], expected[1])
    assert (EX.s, EX.p, value) in data


def test_report_clone_warning_as_error_precedes_inplace_rule_commit(monkeypatch):
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        metadata = Literal("invalid", datatype=XSD.boolean, normalize=False)
    data = Graph()
    data.bind("ex", EX)
    shapes = Graph().parse(
        data="""@prefix ex:<urn:example:>. @prefix sh:<http://www.w3.org/ns/shacl#>.
        ex:S sh:targetNode ex:s;sh:property [sh:path ex:required;sh:minCount 1];
        sh:rule [a sh:TripleRule;sh:subject sh:this;sh:predicate ex:derived;sh:object ex:value].""",
        format="turtle",
    )
    property_shape = shapes.value(EX.S, SH.property)
    shapes.add((property_shape, EX.note, metadata))
    before = set(shapes)
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        with pytest.raises(UserWarning, match="Parsing weird boolean"):
            turbo.validate(data, shacl_graph=shapes, advanced=True, inplace=True)
    assert not data
    assert set(shapes) == before


@pytest.mark.parametrize("normalize", [False, True])
@pytest.mark.parametrize("runner", [False, True])
def test_direct_runner_and_compiled_reports_honor_current_normalization(
    monkeypatch, normalize, runner
):
    from pyshacl.graph_abstraction import DataGraph as ReferenceDataGraph
    from pyshacl_turbo.graph_abstraction import DataGraph

    monkeypatch.setattr(rdflib, "NORMALIZE_LITERALS", normalize)
    data = Graph()
    data.bind("ex", EX)
    shapes = Graph().parse(
        data="""@prefix ex:<urn:example:>. @prefix sh:<http://www.w3.org/ns/shacl#>.
        ex:S sh:targetNode ex:s;sh:property [sh:path ex:required;sh:minCount 1].""",
        format="turtle",
    )
    note = Literal("+001", datatype=XSD.integer, normalize=False)
    shapes.add((shapes.value(EX.S, SH.property), EX.note, note))
    expected = pyshacl.Validator(
        ReferenceDataGraph.from_rdflib_graph(data), shacl_graph=shapes
    ).run()
    assert rdflib.NORMALIZE_LITERALS is normalize
    actual = (
        turbo.Validator(DataGraph.from_rdflib_graph(data), shacl_graph=shapes).run()
        if runner
        else turbo.compile_shapes(shapes).validate(data)
    )
    assert rdflib.NORMALIZE_LITERALS is normalize
    assert actual[2] == expected[2]
    assert isomorphic(actual[1], expected[1])


@pytest.mark.parametrize("normalize", [False, True])
def test_report_copy_policy_preserves_reused_cycles_and_list_paths(monkeypatch, normalize):
    from pyshacl_turbo._report import normalize_native_report_clones

    monkeypatch.setattr(rdflib, "NORMALIZE_LITERALS", normalize)
    report = Graph()
    result, shape, head, tail = (BNode() for _ in range(4))
    integer = Literal("+001", datatype=XSD.integer, normalize=False)
    decimal = Literal("01.20", datatype=XSD.decimal, normalize=False)
    boolean = Literal("1", datatype=XSD.boolean, normalize=False)
    for triple in (
        (result, RDF.type, SH.ValidationResult),
        (result, SH.sourceShape, shape),
        (result, SH.focusNode, shape),
        (result, SH.resultPath, head),
        (result, SH.value, integer),
        (shape, EX.self, shape),
        (shape, EX.value, integer),
        (shape, EX.list, head),
        (head, RDF.first, decimal),
        (head, RDF.rest, tail),
        (tail, RDF.first, boolean),
        (tail, RDF.rest, RDF.nil),
    ):
        report.add(triple)
    assert normalize_native_report_clones(report) is report
    assert len(report) == 12
    assert report.value(result, SH.value) == integer
    assert report.value(shape, EX.self) == shape
    assert report.value(result, SH.focusNode) == report.value(result, SH.sourceShape) == shape
    assert report.value(shape, EX.value) == Literal(str(integer), datatype=XSD.integer)
    assert report.value(head, RDF.first) == Literal(str(decimal), datatype=XSD.decimal)
    assert report.value(tail, RDF.first) == Literal(str(boolean), datatype=XSD.boolean)
    assert list(report.objects(head, RDF.rest)) == [tail]
    assert list(report.objects(tail, RDF.rest)) == [RDF.nil]
    assert rdflib.NORMALIZE_LITERALS is normalize
