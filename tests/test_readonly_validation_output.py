"""Core validation must not export and reconcile an unchanged input relation."""

import pyshacl_turbo as turbo
import pytest
from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.namespace import RDF, SH


@pytest.mark.parametrize("dataset", [False, True])
@pytest.mark.parametrize("inplace", [False, True])
@pytest.mark.parametrize("advanced", [False, True])
def test_core_validation_omits_expanded_input(monkeypatch, dataset, inplace, advanced):
    data = Dataset(default_union=True) if dataset else Graph()
    target = data.default_graph if dataset else data
    subject, predicate = URIRef("urn:focus"), URIRef("urn:p")
    target.add((subject, predicate, Literal("valid")))
    shapes = Graph().parse(
        data="""
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        <urn:shape> sh:targetNode <urn:focus> ;
            sh:property [ sh:path <urn:p> ; sh:minCount 1 ] .
        """,
        format="turtle",
    )
    program = turbo.CompiledShapes(shapes, advanced=advanced)
    native = program._native
    exported = []
    commits = []
    commit = turbo.commit_serialized

    class NativeSpy:
        selected_frames_only = native.selected_frames_only

        def validate(self, *args, **kwargs):
            result = native.validate(*args, **kwargs)
            exported.append((args[6], result[3]))
            return result

    def record_commit(*args, **kwargs):
        commits.append(True)
        return commit(*args, **kwargs)

    program._native = NativeSpy()
    monkeypatch.setattr(turbo, "commit_serialized", record_commit)
    conforms, report, _ = program.validate(data, inplace=inplace)
    assert conforms is True
    root = next(report.subjects(RDF.type, SH.ValidationReport))
    assert report.value(root, SH.conforms) == Literal(True)
    assert set(target) == {(subject, predicate, Literal("valid"))}
    assert len(exported) == 1
    if advanced and inplace:
        assert exported[0][0] is True
        assert exported[0][1] is not None
        assert commits == [True]
    else:
        assert exported == [(False, None)]
        assert commits == []


def test_advanced_rule_validation_keeps_inplace_effects():
    subject, predicate, added = map(URIRef, ("urn:focus", "urn:p", "urn:added"))
    data = Graph()
    data.add((subject, predicate, Literal("input")))
    shapes = Graph().parse(
        data="""
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        <urn:shape> a sh:NodeShape ; sh:targetNode <urn:focus> ;
            sh:rule [ a sh:TripleRule ; sh:subject sh:this ;
                sh:predicate <urn:added> ; sh:object "derived" ] .
        """,
        format="turtle",
    )
    conforms, _, _ = turbo.validate(data, shacl_graph=shapes, advanced=True, inplace=True)
    assert conforms is True
    assert set(data) == {
        (subject, predicate, Literal("input")),
        (subject, added, Literal("derived")),
    }
    assert (URIRef("urn:shape"), RDF.type, SH.NodeShape) in shapes
