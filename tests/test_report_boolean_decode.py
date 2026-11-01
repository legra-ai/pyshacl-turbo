"""Generated report booleans are selected by occurrence, never term index alone."""

import pytest
from pyshacl_turbo.rdf import decode
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import RDF, SH, XSD


def payload(conforms=False, context=None):
    records = [
        (1, "root", None, None),
        (0, str(RDF.type), None, None),
        (0, str(SH.ValidationReport), None, None),
        (0, str(SH.conforms), None, None),
        (2, "true" if conforms else "false", str(XSD.boolean), None),
    ]
    if context is not None:
        records.append((0, str(context), None, None))
    graph = None if context is None else 5
    return records, [(0, 1, 2, graph), (0, 3, 4, graph)]


@pytest.mark.parametrize("conforms", [False, True])
@pytest.mark.parametrize("context", [None, URIRef("urn:report")])
def test_generated_root_at_subject_zero_uses_actual_boolean_in_its_context(conforms, context):
    source = payload(conforms, context)
    graph = decode(source, preserve_ids=True, report=True, _report_conforms=conforms)
    target = graph if context is None else graph.graph(context)
    value = target.value(BNode("root"), SH.conforms)
    assert str(value) == ("true" if conforms else "false")
    assert value.datatype == XSD.boolean and value.language is None
    assert type(value.value) is bool and value.value is conforms and value.ill_typed is None


def test_header_message_and_copied_root_share_one_record_without_sharing_cache_policy():
    records, quads = payload()
    records.extend(
        [
            (1, "result", None, None),
            (0, str(SH.ValidationResult), None, None),
            (0, str(SH.resultMessage), None, None),
            (0, str(SH.sourceShape), None, None),
            (1, "copied-root", None, None),
        ]
    )
    quads.extend(
        [(5, 1, 6, None), (5, 7, 4, None), (5, 8, 9, None), (9, 1, 2, None), (9, 3, 4, None)]
    )
    graph = decode((records, quads), preserve_ids=True, report=True, _report_conforms=False)
    generated = graph.value(BNode("root"), SH.conforms)
    message = graph.value(BNode("result"), SH.resultMessage)
    copied = graph.value(BNode("copied-root"), SH.conforms)
    assert generated.ill_typed is None
    assert message.ill_typed is False and copied.ill_typed is False
    assert generated == message == copied == Literal(False)
    assert generated is not message and generated is not copied


@pytest.mark.parametrize("report", [False, True])
def test_no_native_conformance_hint_preserves_existing_partial_and_nonreport_decoding(report):
    source = payload()
    graph = decode(source, preserve_ids=True, report=report)
    assert graph.value(BNode("root"), SH.conforms).ill_typed is False
    graph = decode((source[0], source[1][1:]), preserve_ids=True, report=report)
    assert graph.value(BNode("root"), SH.conforms).ill_typed is False


@pytest.mark.parametrize("conforms", [0, 1, "false", object()])
def test_full_report_context_rejects_non_boolean_status(conforms):
    with pytest.raises(TypeError, match="boolean"):
        decode(payload(), report=True, _report_conforms=conforms)


@pytest.mark.parametrize(
    "defect",
    [
        "missing_root",
        "missing_status",
        "multiple_roots",
        "duplicate_status",
        "datatype",
        "language",
        "lexical",
        "status_mismatch",
        "kind",
        "context",
    ],
)
def test_malformed_full_native_header_fails_without_canonical_fallback(defect):
    records, quads = payload()
    if defect == "missing_root":
        quads.pop(0)
    elif defect == "missing_status":
        quads.pop()
    elif defect == "multiple_roots":
        records.append((1, "other-root", None, None))
        quads.append((5, 1, 2, None))
    elif defect == "duplicate_status":
        quads.append(quads[-1])
    elif defect == "context":
        records.append((0, "urn:other-context", None, None))
        quads[-1] = (0, 3, 4, 5)
    else:
        records[4] = {
            "datatype": (2, "false", str(XSD.string), None),
            "language": (2, "false", str(XSD.boolean), "en"),
            "lexical": (2, "0", str(XSD.boolean), None),
            "status_mismatch": (2, "true", str(XSD.boolean), None),
            "kind": (0, "false", None, None),
        }[defect]
    with pytest.raises(ValueError, match="report"):
        decode((records, quads), report=True, _report_conforms=False)


def test_native_conformance_context_is_rejected_for_nonreport_output():
    with pytest.raises(ValueError, match="report"):
        decode(payload(), _report_conforms=False)


def test_native_list_frames_preserve_generated_boolean_occurrence():
    records, quads = payload()
    graph = decode(
        ([list(record) for record in records], [list(quad) for quad in quads]),
        preserve_ids=True,
        report=True,
        _report_conforms=False,
    )
    assert graph.value(BNode("root"), SH.conforms).ill_typed is None


@pytest.mark.parametrize("status", [None, 0, 1, "false"])
@pytest.mark.parametrize("shared", [False, True])
def test_full_validation_boundary_rejects_invalid_status_before_warning_materialization(
    status, shared, monkeypatch
):
    from contextlib import nullcontext
    from types import SimpleNamespace

    import pyshacl_turbo as turbo
    from rdflib import Graph

    program = turbo.compile_shapes(Graph())
    calls = []
    monkeypatch.setattr(turbo, "_emit_recursion_warnings", lambda value: calls.append(value))
    if shared:

        class NativeGraphView(Graph):
            def _validate_shared_shapes(self, compiled, settings, inplace):
                return nullcontext((status, payload(), "", []))

        data = NativeGraphView()
        program._shared_program = object()
    else:
        data = Graph()
        program._native = SimpleNamespace(
            selected_frames_only=program._native.selected_frames_only,
            validate=lambda *args, **kwargs: (status, payload(), "", "", []),
        )
    with pytest.raises(TypeError, match="conformance must be a boolean"):
        program.validate(data)
    assert calls == []
