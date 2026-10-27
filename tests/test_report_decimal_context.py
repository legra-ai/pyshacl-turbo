"""Report restoration preserves caller signals and actual description-copy effects."""

import decimal

import pyshacl
import pyshacl_turbo
import pytest
from rdflib import BNode, Graph, Literal, Namespace
from rdflib import Dataset as ReferenceDataset
from rdflib.namespace import SH, XSD
from rdflib_turbo import StoreDataset

EX = Namespace("urn:report-decimal-context:")


def observe_report(implementation, route, role, float_trap, seeded):
    with decimal.localcontext() as context:
        # This is the default cache-None construction profile of the demonstrated 14 cases.
        context.traps[decimal.InvalidOperation] = True
        context.traps[decimal.FloatOperation] = float_trap
        owner = (
            (StoreDataset() if implementation is pyshacl_turbo else ReferenceDataset())
            if route == "dataset"
            else Graph()
        )
        data = owner.default_graph if route == "dataset" else owner
        invalid = Literal("not-a-decimal", datatype=XSD.decimal, normalize=False)
        assert invalid.value is None
        assert invalid.ill_typed is True
        shapes = Graph()
        shapes.add((EX.shape, SH.targetNode, EX.focus))
        shapes.add((EX.shape, SH.path, EX.value))
        if role != "direct":
            value = BNode("described")
            data.add((value, EX.detail, invalid))
            shapes.add((EX.shape, SH["class"], EX.Required))
            if role == "both":
                # One native wire term occurs as a direct value and copied description value.
                data.add((EX.focus, EX.value, invalid))
        else:
            value = invalid
            shapes.add((EX.shape, SH.minInclusive, Literal(1.0, datatype=XSD.double)))
        data.add((EX.focus, EX.value, value))
        context.clear_flags()
        if seeded:
            context.flags[decimal.Inexact] = True
            context.flags[decimal.FloatOperation] = True
            context.flags[decimal.InvalidOperation] = True
        configured = str(context)
        try:
            conforms, report, _ = implementation.validate(owner, shacl_graph=shapes)
            flags = {signal.__name__ for signal, active in context.flags.items() if active}
            # Read the already materialized report literal; do not trigger a second decode.
            literals = (
                list(report.objects(None, EX.detail))
                if role != "direct"
                else list(report.objects(None, SH.value))
            )
            assert len(literals) == 1
            restored = literals[0]
            assert isinstance(restored, Literal)
            assert str(restored) == str(invalid)
            assert restored.datatype == invalid.datatype
            assert restored.value is None
            assert restored.ill_typed is True
            if role == "both":
                direct = [
                    term for term in report.objects(None, SH.value) if isinstance(term, Literal)
                ]
                assert len(direct) == 1
                assert direct[0] == restored
                assert direct[0].value is None
                assert direct[0].ill_typed is True
            assert context.traps[decimal.InvalidOperation] is True
            assert context.traps[decimal.FloatOperation] is float_trap
            # Context configuration and all preexisting sticky signals survive presentation.
            assert str(context).split("flags=")[0] == configured.split("flags=")[0]
            return conforms, flags
        finally:
            if implementation is pyshacl_turbo and route == "dataset":
                owner.close()


@pytest.mark.parametrize("route", ["graph", "dataset"])
@pytest.mark.parametrize("role", ["direct", "copied", "both"])
@pytest.mark.parametrize("float_trap", [False, True])
@pytest.mark.parametrize("seeded", [False, True])
def test_report_literals_preserve_role_specific_decimal_context(route, role, float_trap, seeded):
    expected = observe_report(pyshacl, route, role, float_trap, seeded)
    actual = observe_report(pyshacl_turbo, route, role, float_trap, seeded)
    assert actual == expected
    assert expected[0] is False
    expected_flags = {"Inexact", "FloatOperation", "InvalidOperation"} if seeded else set()
    if role != "direct":
        expected_flags.add("InvalidOperation")
    assert expected[1] == expected_flags
