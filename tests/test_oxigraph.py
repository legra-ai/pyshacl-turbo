import pyoxigraph as ox
import pyshacl_turbo as turbo
import pytest
from rdflib import BNode, Literal
from rdflib.namespace import SH
from test_compatibility import EX, PREFIXES, graph


def store(text):
    result = ox.Store()
    result.load(input=PREFIXES + text, format=ox.RdfFormat.TRIG)
    return result


def test_store_input_preserves_named_graphs_and_matches_rdflib(monkeypatch):
    data = store("ex:g { ex:s ex:p 1. }")
    before = set(data)
    shapes = graph("""ex:S sh:targetNode ex:s; sh:sparql [sh:message "named";
      sh:select "SELECT $this WHERE { GRAPH ex:g { $this ex:p ?v } }"].""")
    # The store-to-engine input path must not materialize an RDFLib data graph.
    from pyshacl_turbo import rdf

    original = rdf.decode

    def only_report(source, *args, **kwargs):
        assert str(SH.ValidationReport) in source
        return original(source, *args, **kwargs)

    monkeypatch.setattr(rdf, "decode", only_report)
    conforms, report, _ = turbo.validate(data, shacl_graph=shapes)
    assert not conforms
    assert list(report.objects(None, SH.focusNode)) == [EX.s]
    assert set(data) == before


def test_store_blank_nodes_keep_their_labels_in_the_report():
    data = ox.Store()
    data.add(ox.Quad(ox.BlankNode("person"), ox.NamedNode(str(EX.p)), ox.Literal(1)))
    _, report, _ = turbo.validate(
        data, shacl_graph=graph("ex:S sh:targetSubjectsOf ex:p; sh:path ex:q; sh:minCount 1.")
    )
    assert list(report.objects(None, SH.focusNode)) == [BNode("person")]


@pytest.mark.parametrize("inplace", [False, True])
def test_store_rule_updates_preserve_contexts_and_commit_only_when_requested(inplace):
    data = store("ex:g { ex:s ex:p 1. }")
    shapes = graph("""ex:S sh:targetSubjectsOf ex:p; sh:rule [a sh:SPARQLRule;
      sh:construct "CONSTRUCT { $this ex:derived true } WHERE {}"].""")
    before = set(data)
    output = turbo.shacl_rules(data, shacl_graph=shapes, inplace=inplace)
    derived = ox.Quad(ox.NamedNode(str(EX.s)), ox.NamedNode(str(EX.derived)), ox.Literal(True))
    assert all(q in data for q in before)
    assert (derived in data) is inplace
    assert (EX.s, EX.derived, Literal(True)) in output
    assert set(data) == (before | {derived} if inplace else before)


def test_store_failed_rule_expansion_does_not_commit():
    data = store("ex:s ex:p 1.")
    before = set(data)
    shapes = graph("""ex:S sh:targetSubjectsOf ex:p; sh:rule [a sh:SPARQLRule;
      sh:construct "CONSTRUCT { $this ex:new [] } WHERE {}"].""")
    with pytest.raises(RuntimeError, match="iteration"):
        turbo.validate(
            data,
            shacl_graph=shapes,
            advanced=True,
            inplace=True,
            iterate_rules=True,
            max_rule_iterations=2,
        )
    assert set(data) == before


def test_store_native_inference_does_not_construct_rdflib_input(monkeypatch):
    data = store("ex:A rdfs:subClassOf ex:B. ex:s a ex:A.")
    shapes = graph("ex:S sh:targetClass ex:B; sh:path ex:p; sh:minCount 1.")
    original = turbo._graph

    def only_report(source, *args, **kwargs):
        assert str(SH.ValidationReport) in source
        return original(source, *args, **kwargs)

    monkeypatch.setattr(turbo, "_graph", only_report)
    conforms, report, _ = turbo.validate(data, shacl_graph=shapes, inference="rdfs", inplace=True)
    assert not conforms
    assert list(report.objects(None, SH.focusNode)) == [EX.s]
    assert (
        ox.Quad(
            ox.NamedNode(str(EX.s)),
            ox.NamedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            ox.NamedNode(str(EX.B)),
            ox.NamedNode("urn:pyshacl:inference"),
        )
        in data
    )


def test_store_can_supply_shapes_too():
    shapes = store("ex:g { ex:S sh:targetNode ex:s; sh:path ex:p; sh:minCount 1. }")
    assert not turbo.validate(ox.Store(), shacl_graph=shapes)[0]


@pytest.mark.parametrize("inference", [None, "rdfs"])
def test_store_commit_does_not_restore_a_concurrently_deleted_input_quad(monkeypatch, inference):
    data = store("ex:s ex:p 1.")
    original_quad = next(iter(data))
    shapes = graph("""ex:S sh:targetNode ex:s; sh:rule [a sh:SPARQLRule;
      sh:construct "CONSTRUCT { $this ex:derived true } WHERE {}"].""")
    commit = turbo.commit_serialized

    def concurrent_delete(target, *args, **kwargs):
        if target is data:
            data.remove(original_quad)
        return commit(target, *args, **kwargs)

    monkeypatch.setattr(turbo, "commit_serialized", concurrent_delete)
    turbo.validate(data, shacl_graph=shapes, advanced=True, inference=inference, inplace=True)
    assert original_quad not in data
    assert ox.Quad(ox.NamedNode(str(EX.s)), ox.NamedNode(str(EX.derived)), ox.Literal(True)) in data
