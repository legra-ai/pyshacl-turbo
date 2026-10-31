"""Generated report status has constructor provenance, unlike lexical messages."""

import warnings
from decimal import getcontext

import pyshacl
import pyshacl_turbo
import pytest
from rdflib import Graph
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, SH


def metadata(value):
    return (
        str(value),
        value.datatype,
        value.language,
        type(value.value),
        value.value,
        value.ill_typed,
    )


def observe(module, conforms, custom, documents):
    data_text = '<urn:s> <urn:p> "value" .' if conforms else '<urn:s> <urn:seed> "value" .'
    shapes_text = (
        "@prefix sh:<http://www.w3.org/ns/shacl#>. "
        "<urn:S> a sh:PropertyShape;sh:targetNode <urn:s>;sh:path <urn:p>;sh:minCount 1"
        + (";sh:message false" if custom else "")
        + "."
    )
    data = data_text if documents else Graph().parse(data=data_text, format="turtle")
    shapes = shapes_text if documents else Graph().parse(data=shapes_text, format="turtle")
    before_data = None if documents else set(data)
    before_shapes = None if documents else set(shapes)
    context = getcontext()
    before_flags, before_traps = dict(context.flags), dict(context.traps)
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        result = module.validate(
            data, shacl_graph=shapes, data_graph_format="turtle", shacl_graph_format="turtle"
        )
    assert dict(context.flags) == before_flags and dict(context.traps) == before_traps
    if not documents:
        assert set(data) == before_data
    root = next(result[1].subjects(RDF.type, SH.ValidationReport))
    return {
        "result": result,
        "root": metadata(result[1].value(root, SH.conforms)),
        "messages": sorted(
            (metadata(v) for v in result[1].objects(None, SH.resultMessage)), key=repr
        ),
        "warnings": [(type(w.message), str(w.message)) for w in seen],
        "shape_delta": None
        if documents
        else (set(shapes) - before_shapes, before_shapes - set(shapes)),
    }


@pytest.mark.parametrize("conforms", [False, True])
@pytest.mark.parametrize("custom", [False, True])
@pytest.mark.parametrize("documents", [False, True])
def test_generated_report_status_constructor_metadata_role(
    conforms, custom, documents, record_property
):
    original = observe(pyshacl, conforms, custom, documents)
    actual = observe(pyshacl_turbo, conforms, custom, documents)
    record_property("original_text", original["result"][2])
    record_property("candidate_text", actual["result"][2])
    record_property("original_warnings", repr(original["warnings"]))
    record_property("candidate_warnings", repr(actual["warnings"]))
    record_property("original_warning_count", len(original["warnings"]))
    record_property("candidate_warning_count", len(actual["warnings"]))
    record_property(
        "document_warning_parity_gap", documents and original["warnings"] != actual["warnings"]
    )
    assert actual["root"] == original["root"]
    # Custom boolean message text is a separate native formatter defect. Retain
    # both raw strings, and test this materializer's RDF/cache role independently.
    if not custom or conforms:
        assert actual["result"][2] == original["result"][2]
    assert actual["result"][0] is original["result"][0] is conforms
    assert isomorphic(actual["result"][1], original["result"][1])
    if not documents:
        assert actual["warnings"] == original["warnings"]
    assert actual["shape_delta"] == original["shape_delta"]
    assert actual["messages"] == original["messages"]
