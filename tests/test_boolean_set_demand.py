"""The demanded value set owns actual hash/equality and iteration semantics."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SH, XSD


@pytest.mark.parametrize(
    "kind",
    ["distinct-forward", "distinct-reverse", "duplicate-good-first", "duplicate-bad-first"],
)
def test_selected_acquisition_preserves_actual_set_events_and_owner_order(kind):
    def observe(validator):
        events = []
        active = False

        class Observed(Literal):
            def __hash__(self):
                if active:
                    events.append(("hash", str(self)))
                return Literal.__hash__(self)

            def __eq__(self, other):
                if active:
                    events.append(("equal", str(self), str(other)))
                return Literal.__eq__(self, other)

            @property
            def ill_typed(self):
                events.append(("ill_typed", str(self)))
                return Literal.ill_typed.fget(self)

            @property
            def value(self):
                events.append(("value", str(self)))
                return Literal.value.fget(self)

        good = Observed("false", datatype=XSD.boolean, normalize=False)
        other = Observed(
            "true" if kind.startswith("distinct") else "none",
            datatype=XSD.boolean,
            normalize=not kind.startswith("distinct"),
        )
        selected = [good, other]
        if kind in ("distinct-reverse", "duplicate-bad-first"):
            selected.reverse()
        subject, predicate = URIRef("urn:s"), URIRef("urn:p")

        class Selected(Graph):
            def triples(self, pattern):
                if pattern == (subject, predicate, None):

                    def values():
                        nonlocal active
                        active = True
                        events.append(("begin",))
                        try:
                            for value in selected:
                                yield subject, predicate, value
                        finally:
                            events.append(("end",))
                            active = False

                    return values()
                return super().triples(pattern)

        data = Selected()
        data.add((subject, predicate, good))
        events.clear()
        shape = Graph().parse(
            data="@prefix sh:<http://www.w3.org/ns/shacl#>. "
            "@prefix xsd:<http://www.w3.org/2001/XMLSchema#>. "
            "<urn:S> sh:targetNode <urn:s>;sh:path <urn:p>;sh:datatype xsd:boolean.",
            format="turtle",
        )
        out = validator(data, shacl_graph=shape)
        reported = list(out[1].objects(None, SH.value))
        if kind == "duplicate-bad-first":
            assert reported and all(value is selected[0] for value in reported)
        else:
            assert reported == []
        return events, out[0], len(out[1]), out[2]

    expected = observe(pyshacl.validate)
    actual = observe(turbo.validate)
    assert actual == expected
