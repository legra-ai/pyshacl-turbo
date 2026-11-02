"""Predicate acquisition calls the actual ordinary Graph.objects API."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SH, XSD


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize("kind", ["selected", "error", "inherited-subject"])
def test_actual_objects_owner_error_and_inherited_subject(validator, kind):
    subject, predicate = URIRef("urn:s"), URIRef("urn:p")
    selected = Literal("none", datatype=XSD.boolean, normalize=True)
    failure = LookupError("actual objects acquisition", 51)
    events = []

    class Selected(Graph):
        def objects(self, focus=None, path=None, unique=False):
            if focus == subject and path == predicate:
                events.append(("objects", str(focus), str(path), unique))
                if kind == "error":
                    raise failure
                return iter([selected])
            if path == URIRef("urn:q"):
                events.append(("inherited", focus is selected))
                return iter(())
            return super().objects(focus, path, unique)

        def triples(self, pattern):
            if pattern[0] is not None and pattern[1] is not None and pattern[2] is None:
                raise AssertionError("The overridden objects route must not query triples")
            return super().triples(pattern)

    data = Selected()
    data.add((subject, predicate, Literal("false", datatype=XSD.boolean, normalize=False)))
    constraint = (
        "sh:property [sh:path <urn:q>;sh:minCount 1]"
        if kind == "inherited-subject"
        else "sh:datatype xsd:boolean"
    )
    shape = Graph().parse(
        data="@prefix sh:<http://www.w3.org/ns/shacl#>. "
        "@prefix xsd:<http://www.w3.org/2001/XMLSchema#>. "
        f"<urn:S> sh:targetNode <urn:s>;sh:path <urn:p>;{constraint}.",
        format="turtle",
    )
    if kind == "error":
        with pytest.raises(LookupError) as observed:
            validator(data, shacl_graph=shape)
        assert observed.value is failure
        assert observed.value.args == ("actual objects acquisition", 51)
        assert observed.value.__context__ is None
    else:
        result = validator(data, shacl_graph=shape)
        assert result[0] is False
        role = SH.focusNode if kind == "inherited-subject" else SH.value
        assert list(result[1].objects(None, role)) == [selected]
        assert next(result[1].objects(None, role)) is selected
        assert len(result[1]) == (12 if kind == "inherited-subject" else 11)
    assert events == [("objects", "urn:s", "urn:p", False)] + (
        [("inherited", True)] if kind == "inherited-subject" else []
    )
