"""Selected Boolean acquisition follows actual shape demand, not input size."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import XSD


def shapes(body):
    return Graph().parse(
        data="""@prefix sh:<http://www.w3.org/ns/shacl#>.
        @prefix xsd:<http://www.w3.org/2001/XMLSchema#>.
        """
        + body,
        format="turtle",
    )


def run(validator, body, *, allowed=None, value_factory=None, **options):
    events = []
    failure = LookupError("unrequested selected read", 41)

    class Watched(Graph):
        def triples(self, pattern):
            subject, predicate, obj = pattern
            if subject is not None and predicate is not None and obj is None:
                key = (str(subject), str(predicate))
                events.append(("sp", *key))
                if allowed is not None and key not in allowed:
                    raise failure
            return super().triples(pattern)

    data = Watched()
    value = (
        value_factory(events)
        if value_factory is not None
        else Literal("false", datatype=XSD.boolean, normalize=False)
    )
    for index in range(4):
        data.add((URIRef(f"urn:s{index}"), URIRef("urn:p"), value))
    events.clear()
    try:
        result = validator(data, shacl_graph=shapes(body), **options)
    except LookupError as error:
        assert error is failure
        assert error.args == ("unrequested selected read", 41)
        return events, error
    return events, (result[0], len(result[1]), result[2])


@pytest.mark.parametrize(
    "body,options,allowed,expected_calls",
    [
        (
            "<urn:S> sh:targetNode <urn:s0>;sh:path <urn:p>;sh:datatype xsd:boolean.",
            {},
            {("urn:s0", "urn:p")},
            [("sp", "urn:s0", "urn:p")],
        ),
        (
            "<urn:S> sh:targetNode <urn:s0>;sh:path <urn:p>;sh:datatype xsd:boolean.",
            {"focus_nodes": ["urn:absent"]},
            set(),
            [],
        ),
        (
            "<urn:S> sh:targetNode <urn:s0>;sh:path <urn:p>;sh:deactivated true.",
            {},
            set(),
            [],
        ),
        (
            "<urn:S> sh:targetNode <urn:s0>;sh:path <urn:q>;sh:datatype xsd:boolean.",
            {},
            {("urn:s0", "urn:q")},
            [("sp", "urn:s0", "urn:q")],
        ),
    ],
)
def test_only_actual_shape_demand_reads_selected_sp(body, options, allowed, expected_calls):
    expected = run(pyshacl.validate, body, allowed=allowed, **options)
    assert expected[0] == expected_calls
    assert not isinstance(expected[1], Exception)
    actual = run(turbo.validate, body, allowed=allowed, **options)
    assert actual == expected


@pytest.mark.parametrize(
    "body,options",
    [
        (
            """<urn:S> sh:targetNode <urn:s0>;sh:path <urn:p>;
        sh:datatype xsd:boolean;sh:nodeKind sh:Literal;sh:minCount 1;sh:maxCount 1.""",
            {},
        ),
        (
            """<urn:S> a sh:PropertyShape;sh:path <urn:p>;
        sh:qualifiedValueShape [sh:nodeKind sh:Literal];sh:qualifiedMinCount 1.""",
            {"use_shapes": ["urn:S"], "focus_nodes": ["urn:s0", "urn:s1"]},
        ),
        (
            """<urn:S> sh:targetNode <urn:s0>;sh:property <urn:A>,<urn:B>.
        <urn:A> sh:path <urn:p>;sh:datatype xsd:boolean.
        <urn:B> sh:path <urn:p>;sh:nodeKind sh:Literal.""",
            {},
        ),
    ],
)
def test_constraints_qualified_and_nested_invocations_preserve_read_counts(body, options):
    expected = run(pyshacl.validate, body, **options)
    actual = run(turbo.validate, body, **options)
    assert actual == expected


@pytest.mark.parametrize(
    "constraint,invalid",
    [
        ("sh:nodeKind sh:Literal", False),
        ("sh:datatype xsd:boolean", False),
        ("sh:datatype xsd:boolean", True),
    ],
)
def test_assessment_getters_are_deferred_to_actual_consumers(constraint, invalid):
    def value_factory(events):
        class Observed(Literal):
            @property
            def value(self):
                events.append(("value",))
                return Literal.value.fget(self)

            @property
            def ill_typed(self):
                events.append(("ill_typed",))
                return Literal.ill_typed.fget(self)

        return Observed("none" if invalid else "false", datatype=XSD.boolean, normalize=invalid)

    body = f"<urn:S> sh:targetNode <urn:s0>;sh:path <urn:p>;{constraint}."
    expected = run(pyshacl.validate, body, value_factory=value_factory)
    actual = run(turbo.validate, body, value_factory=value_factory)
    assert actual == expected


def test_requested_callback_error_keeps_exact_exception():
    body = "<urn:S> sh:targetNode <urn:s0>;sh:path <urn:p>;sh:datatype xsd:boolean."
    for validator in (pyshacl.validate, turbo.validate):
        events, error = run(validator, body, allowed=set())
        assert isinstance(error, LookupError)
        assert events == [("sp", "urn:s0", "urn:p")]


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize("abort_first", [False, True])
def test_cache_getter_error_is_skipped_by_earlier_aborting_count(abort_first, validator):
    events = []
    failure = LookupError("actual deferred value getter", 73)

    class Deferred(Literal):
        @property
        def ill_typed(self):
            events.append("ill_typed")
            return False

        @property
        def value(self):
            events.append("value")
            raise failure

    data = Graph()
    data.add(
        (
            URIRef("urn:s0"),
            URIRef("urn:p"),
            Deferred("false", datatype=XSD.boolean, normalize=False),
        )
    )
    shape = shapes(
        """<urn:S> sh:targetNode <urn:s0>;sh:path <urn:p>;
        sh:minCount 2;sh:datatype xsd:boolean."""
    )
    if abort_first:
        result = validator(data, shacl_graph=shape, abort_on_first=True)
        assert result[0] is False
        assert events == []
    else:
        with pytest.raises(LookupError) as observed:
            validator(data, shacl_graph=shape)
        assert observed.value is failure
        assert observed.value.args == ("actual deferred value getter", 73)
        assert events == ["ill_typed", "value"]


@pytest.mark.parametrize(
    "nested",
    [
        "sh:node [sh:datatype xsd:boolean]",
        "sh:qualifiedValueShape [sh:datatype xsd:boolean];sh:qualifiedMinCount 1",
    ],
)
def test_nested_datatype_consumes_the_actual_parent_selected_owner(nested):
    data = Graph()
    data.add(
        (
            URIRef("urn:s0"),
            URIRef("urn:p"),
            Literal("none", datatype=XSD.boolean, normalize=True),
        )
    )
    shape = shapes(f"<urn:S> sh:targetNode <urn:s0>;sh:path <urn:p>;{nested}.")
    expected = pyshacl.validate(data, shacl_graph=shape)
    assert expected[0] is False
    actual = turbo.validate(data, shacl_graph=shape)
    assert actual[0] is False
    assert len(actual[1]) == len(expected[1])
    assert actual[2] == expected[2]


def test_explicit_focus_batch_acquires_all_values_before_assessment():
    def value_factory(events):
        class Observed(Literal):
            @property
            def ill_typed(self):
                events.append(("ill_typed",))
                return False

            @property
            def value(self):
                events.append(("value",))
                return False

        return Observed("false", datatype=XSD.boolean, normalize=False)

    body = (
        "<urn:S> a sh:PropertyShape;sh:path <urn:p>;sh:datatype xsd:boolean;sh:nodeKind sh:Literal."
    )
    options = {"use_shapes": ["urn:S"], "focus_nodes": ["urn:s1", "urn:s0"]}
    expected = run(pyshacl.validate, body, value_factory=value_factory, **options)
    assert expected[0] == [
        ("sp", "urn:s1", "urn:p"),
        ("sp", "urn:s0", "urn:p"),
        ("ill_typed",),
        ("value",),
        ("ill_typed",),
        ("value",),
    ]
    actual = run(turbo.validate, body, value_factory=value_factory, **options)
    assert actual == expected
