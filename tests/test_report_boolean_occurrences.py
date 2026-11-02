"""Sparse native report attestations must be occurrence scoped and fail closed."""

import pytest
from pyshacl_turbo.rdf import decode
from rdflib import BNode, URIRef
from rdflib.namespace import RDF, SH, XSD


def frame(context=None):
    records = [
        (1, "result", None, None),
        (0, str(RDF.type), None, None),
        (0, str(SH.ValidationResult), None, None),
        (0, str(SH.value), None, None),
        (2, "false", str(XSD.boolean), None),
        (0, "urn:report-context", None, None),
    ]
    return records, [(0, 1, 2, context), (0, 3, 4, context)]


@pytest.mark.parametrize("context", [None, 5])
@pytest.mark.parametrize(
    "code,cached,assessment",
    [
        (1, False, None),
        (2, False, False),
        (3, False, True),
        (4, True, None),
        (5, True, False),
        (6, True, True),
    ],
)
def test_attested_value_preserves_cache_even_when_lexical_word_disagrees(
    code, cached, assessment, context
):
    records, quads = frame(context)
    # The same RDF term in an unrelated occurrence must not inherit the attestation.
    quads.append((0, 1, 4, context))
    graph = decode((records, quads, [(1, code)]), preserve_ids=True, report=True)
    target = graph if context is None else graph.graph(URIRef("urn:report-context"))
    value = target.value(BNode("result"), SH.value)
    unrelated = next(v for v in target.objects(BNode("result"), RDF.type) if str(v) == "false")
    assert str(value) == "false" and value.datatype == XSD.boolean
    assert value.value is cached and value.ill_typed is assessment
    assert unrelated.value is False and unrelated.ill_typed is False
    assert value is not unrelated


@pytest.mark.parametrize(
    "entries,message",
    [
        ([None], "occurrence"),
        ([[]], "occurrence"),
        ([[1, 2, 3]], "occurrence"),
        ([[True, 1]], "index"),
        ([[-1, 1]], "index"),
        ([[2, 1]], "index"),
        ([[1, True]], "state"),
        ([[1, 0]], "state"),
        ([[1, 7]], "state"),
        ([[1, 1], [1, 2]], "state"),
    ],
)
def test_corrupt_sparse_attestation_is_rejected(entries, message):
    with pytest.raises(ValueError, match=message):
        decode((*frame(), entries), report=True)


@pytest.mark.parametrize("defect", ["predicate", "kind", "word", "datatype", "language", "context"])
def test_attestation_cannot_be_applied_to_a_different_report_role(defect):
    records, quads = frame()
    if defect == "predicate":
        quads[1] = (0, 1, 4, None)
    elif defect == "context":
        quads[1] = (0, 3, 4, 5)
    else:
        records[4] = {
            "kind": (0, "false", None, None),
            "word": (2, "0", str(XSD.boolean), None),
            "datatype": (2, "false", str(XSD.string), None),
            "language": (2, "false", str(XSD.boolean), "en"),
        }[defect]
    with pytest.raises(ValueError, match="direct ValidationResult value"):
        decode((records, quads, [(1, 1)]), report=True)
