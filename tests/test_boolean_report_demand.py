"""Reporting consumes actual selected owners at each result creation."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SH, XSD


def shapes(body):
    return Graph().parse(
        data="@prefix sh:<http://www.w3.org/ns/shacl#>. "
        "@prefix xsd:<http://www.w3.org/2001/XMLSchema#>. " + body,
        format="turtle",
    )


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
def test_report_presentation_preserves_exact_first_getter_error(validator):
    events = []
    failure = RuntimeError("actual report value getter", 31)

    class Observed(Literal):
        @property
        def ill_typed(self):
            events.append("ill_typed")
            return True

        @property
        def value(self):
            events.append("value")
            raise failure

    data = Graph()
    data.add(
        (URIRef("urn:s"), URIRef("urn:p"), Observed("false", datatype=XSD.boolean, normalize=False))
    )
    with pytest.raises(RuntimeError) as observed:
        validator(
            data,
            shacl_graph=shapes(
                "<urn:S> sh:targetNode <urn:s>;sh:path <urn:p>;sh:datatype xsd:boolean."
            ),
        )
    assert observed.value is failure
    assert events == ["ill_typed", "value"]


@pytest.mark.parametrize("error_type", [LookupError, ValueError])
def test_report_presentation_specific_fallback_is_actual_lexical_text(error_type):
    def observe(validator):
        events = []

        class Observed(Literal):
            @property
            def ill_typed(self):
                return True

            @property
            def value(self):
                events.append("value")
                raise error_type("formatter fallback")

        data = Graph()
        data.add(
            (
                URIRef("urn:s"),
                URIRef("urn:p"),
                Observed("false", datatype=XSD.boolean, normalize=False),
            )
        )
        out = validator(
            data,
            shacl_graph=shapes(
                "<urn:S> sh:targetNode <urn:s>;sh:path <urn:p>;sh:datatype xsd:boolean."
            ),
        )
        return (out[0], len(out[1]), out[2], events)

    outcomes = [observe(pyshacl.validate), observe(turbo.validate)]
    assert outcomes[0] == outcomes[1]
    assert outcomes[0][3] == ["value"]


def test_nested_focus_and_value_keep_the_same_actual_literal_owner():
    outcomes = []
    for validator in (pyshacl.validate, turbo.validate):
        value = Literal("none", datatype=XSD.boolean, normalize=True)
        data = Graph()
        data.add((URIRef("urn:s"), URIRef("urn:p"), value))
        out = validator(
            data,
            shacl_graph=shapes(
                "<urn:S> sh:targetNode <urn:s>;sh:path <urn:p>;sh:node [sh:datatype xsd:boolean]."
            ),
        )
        assert out[0] is False
        for predicate in (SH.focusNode, SH.value):
            selected = [v for v in out[1].objects(None, predicate) if isinstance(v, Literal)]
            assert selected and all(v is value for v in selected)
        outcomes.append((len(out[1]), out[2]))
    # The inherited shape-message quoting frontier is tested separately.
    assert outcomes[0][0] == outcomes[1][0]


def test_nested_predicate_echoes_inherited_literal_subject_without_recreation():
    def observe(validator):
        events = []
        value = Literal("none", datatype=XSD.boolean, normalize=True)

        class Watched(Graph):
            def triples(self, pattern):
                if pattern[1] == URIRef("urn:q"):
                    events.append(pattern[0] is value)
                return super().triples(pattern)

        data = Watched()
        data.add((URIRef("urn:s"), URIRef("urn:p"), value))
        out = validator(
            data,
            shacl_graph=shapes(
                "<urn:S> sh:targetNode <urn:s>;sh:path <urn:p>;sh:property [sh:path <urn:q>;sh:minCount 1]."
            ),
        )
        assert events == [True]
        assert all(v is value for v in out[1].objects(None, SH.focusNode))
        return (out[0], len(out[1]), out[2])

    outcomes = [observe(pyshacl.validate), observe(turbo.validate)]
    assert outcomes[0] == outcomes[1]


def test_report_uses_the_actual_second_value_read_and_codec_adds_no_getters():
    def observe(validator):
        events = []

        class Observed(Literal):
            @property
            def ill_typed(self):
                events.append("ill_typed")
                return True

            @property
            def value(self):
                events.append("value")
                return "first-read" if events.count("value") == 1 else "actual-second"

        value = Observed("false", datatype=XSD.boolean, normalize=False)
        data = Graph()
        data.add((URIRef("urn:s"), URIRef("urn:p"), value))
        out = validator(
            data,
            shacl_graph=shapes(
                "<urn:S> sh:targetNode <urn:s>;sh:path <urn:p>;sh:datatype xsd:boolean."
            ),
        )
        assert list(out[1].objects(None, SH.value)) == [value]
        assert next(out[1].objects(None, SH.value)) is value
        assert events == ["ill_typed", "value", "value"]
        assert '"false" = actual-second' in out[2]
        return (out[0], len(out[1]), out[2])

    outcomes = [observe(pyshacl.validate), observe(turbo.validate)]
    assert outcomes[0] == outcomes[1]


def test_discarded_qualified_child_reports_still_present_focus_then_value():
    def observe(validator):
        events = []

        class Observed(Literal):
            @property
            def ill_typed(self):
                events.append("ill_typed")
                return True

            @property
            def value(self):
                events.append("value")
                return False

        data = Graph()
        data.add(
            (
                URIRef("urn:s"),
                URIRef("urn:p"),
                Observed("false", datatype=XSD.boolean, normalize=False),
            )
        )
        out = validator(
            data,
            shacl_graph=shapes(
                "<urn:S> sh:targetNode <urn:s>;sh:path <urn:p>;sh:qualifiedValueShape [sh:datatype xsd:boolean];sh:qualifiedMinCount 1."
            ),
        )
        return (out[0], len(out[1]), events)

    observations = [observe(pyshacl.validate), observe(turbo.validate)]
    assert observations[0] == observations[1]
    assert observations[0][2] == ["ill_typed", "value", "value", "value", "value"]
