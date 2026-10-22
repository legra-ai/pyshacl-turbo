"""Report-clone signals reject staged native output before owner acceptance."""

import warnings

import pyshacl_turbo as turbo
import pytest
import rdflib_turbo
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import SH, XSD

EX = Namespace("urn:example:")


@pytest.mark.parametrize("kind", ["dataset", "graph"])
def test_shared_report_clone_rejection_discards_staged_rules(monkeypatch, kind):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        note = Literal("invalid", datatype=XSD.boolean, normalize=False)
    shapes = Graph().parse(
        data="""@prefix ex:<urn:example:>. @prefix sh:<http://www.w3.org/ns/shacl#>.
        ex:S sh:targetNode ex:s;sh:property [sh:path ex:required;sh:minCount 1];
        sh:rule [a sh:TripleRule;sh:subject sh:this;sh:predicate ex:derived;sh:object ex:value].""",
        format="turtle",
    )
    shapes.add((shapes.value(EX.S, SH.property), EX.note, note))
    data = rdflib_turbo.Dataset() if kind == "dataset" else rdflib_turbo.Graph()
    if kind == "dataset":
        owner = data._native
        before = set(data.to_rdflib().quads())
    else:
        owner = data.store.backend._native
        before = set(data)

    def reject_copy(self):
        raise ValueError("caller rejected report clone")

    monkeypatch.setattr(Literal, "normalize", reject_copy)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with pytest.raises(ValueError, match="caller rejected report clone"):
            turbo.validate(data, shacl_graph=shapes, advanced=True, inplace=True)
    if kind == "dataset":
        assert data._native is owner
        assert set(data.to_rdflib().quads()) == before
    else:
        assert data.store.backend._native is owner
        assert set(data) == before
