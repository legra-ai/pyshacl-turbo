"""RDFLib execution transfers exact RDF terms without an RDF text round trip."""

import pyshacl_turbo as turbo
import pytest
from pyshacl_turbo import rdf
from rdflib import BNode, Dataset, Graph, Literal
from rdflib.namespace import SH, XSD
from test_compatibility import EX, graph


@pytest.mark.parametrize("dataset", [False, True])
@pytest.mark.parametrize("rules", [False, True])
def test_rdflib_execution_avoids_text_serialization_and_output_parsing(dataset, rules, monkeypatch):
    data = Dataset(default_union=True) if dataset else Graph()
    destination = data.graph(BNode("context")) if dataset else data
    subject = BNode("subject")
    values = {
        Literal("01", datatype=XSD.integer, normalize=False),
        Literal("same"),
        Literal("same", datatype=XSD.string),
        Literal("bonjour", lang="fr"),
    }
    for value in values:
        destination.add((subject, EX.p, value))
    compiled = turbo.compile_shapes(
        graph("""ex:S sh:targetSubjectsOf ex:p; sh:path ex:missing; sh:minCount 1;
          sh:rule [a sh:SPARQLRule;
            sh:construct "CONSTRUCT { $this ex:derived ?v } WHERE { $this ex:p ?v }"]."""),
        advanced=True,
    )

    def text_roundtrip(*args, **kwargs):
        pytest.fail("RDFLib execution must transfer terms directly")

    monkeypatch.setattr(Graph, "serialize", text_roundtrip)
    monkeypatch.setattr(rdf.W3CNTriplesParser, "parse", text_roundtrip)
    if rules:
        result = compiled.shacl_rules(data)
        assert set(result.objects(subject, EX.derived)) == values
    else:
        conforms, report, _ = compiled.validate(data)
        assert not conforms
        assert list(report.objects(None, SH.focusNode)) == [subject]
    assert set(destination.objects(subject, EX.p)) == values


def test_direct_batches_support_multigraph_loading_and_blank_node_mapping():
    batch = ([(1, "subject", None, None), (0, str(EX.p), None, None)], [(0, 1, 0, None)])
    nodes = {}
    decoded = rdf.decode(batch, nodes, multigraph=True)
    assert isinstance(decoded, Dataset)
    subject = next(decoded.subjects())
    assert subject != BNode("subject")
    assert nodes["subject"] == subject
    assert rdf.decode(batch, nodes).value(subject, EX.p) == subject
    assert rdf.decode(batch, preserve_ids=True).value(BNode("subject"), EX.p) == BNode("subject")
    with pytest.raises(ValueError, match="Invalid native RDF term record"):
        rdf.decode(([(99, "invalid", None, None)], []))


def test_direct_batches_reject_non_rdf_input_nodes():
    class InvalidGraph(Graph):
        def __iter__(self):
            yield EX.s, EX.p, object()

    with pytest.raises(TypeError, match="Expected an RDFLib"):
        rdf.input_graph(InvalidGraph(), direct=True)


def test_direct_internal_snapshot_can_be_expanded_and_loaded_inplace():
    data = rdf.input_graph(graph("ex:s ex:p 1."), direct=True)
    program = turbo.compile_shapes(
        graph("""ex:S sh:targetNode ex:s; sh:rule [a sh:SPARQLRule;
          sh:construct "CONSTRUCT { $this ex:derived true } WHERE {}"]."""),
        advanced=True,
    )
    result = program.shacl_rules(data, inplace=True)
    assert data.format == "terms"
    assert set(rdf.load_from_source(data)) == set(result)
    assert (EX.s, EX.derived, Literal(True)) in result
