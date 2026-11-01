"""Sequence errors and owner selection remain actual Python path events."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import SH, XSD

S, M, Q, P = map(URIRef, ("urn:s", "urn:m", "urn:q", "urn:p"))


def shapes(constraint, prefix=""):
    return Graph().parse(
        data="@prefix sh:<http://www.w3.org/ns/shacl#>. "
        "@prefix xsd:<http://www.w3.org/2001/XMLSchema#>. "
        f"<urn:S> sh:targetNode <urn:s>;sh:path (<urn:q> <urn:p>);{prefix}{constraint}.",
        format="turtle",
    )


@pytest.mark.parametrize("kind", ["iterator", "hash", "equality"])
def test_actual_sequence_iteration_hash_and_equality_error_identity(kind):
    failure = LookupError("actual sequence event", kind)
    all_events = []

    def make_source(events):
        class Selected(Literal):
            def __hash__(self):
                events.append("hash")
                if kind == "hash":
                    raise failure
                return 17

            def __eq__(self, other):
                events.append("eq")
                raise failure

        values = [
            Selected("false", datatype=XSD.boolean, normalize=False),
            Selected("false", datatype=XSD.boolean, normalize=False),
        ]

        def selected():
            for value in values:
                yield value
                if kind == "iterator":
                    raise failure

        class Source(Graph):
            def objects(self, subject=None, predicate=None, unique=False):
                events.append((str(subject), str(predicate)))
                return iter([M]) if predicate == Q else selected()

        data = Source()
        data.add((S, Q, Literal(False)))
        return data

    for validator in (pyshacl.validate, turbo.validate):
        events = []
        data = make_source(events)
        with pytest.raises(LookupError) as observed:
            validator(data, shacl_graph=shapes("sh:datatype xsd:boolean"))
        assert observed.value is failure
        assert observed.value.args == ("actual sequence event", kind)
        assert observed.value.__context__ is None
        all_events.append(events)
    assert all_events[0] == all_events[1]


@pytest.mark.parametrize("bad_first", [False, True])
def test_equal_rdf_sequence_set_keeps_actual_first_cache_owner(bad_first):
    bad = Literal("none", datatype=XSD.boolean, normalize=True)
    good = Literal("false", datatype=XSD.boolean, normalize=False)
    values = [bad, good] if bad_first else [good, bad]

    class Source(Graph):
        def objects(self, subject=None, predicate=None, unique=False):
            return iter([M]) if predicate == Q else iter(values)

    for validator in (pyshacl.validate, turbo.validate):
        data = Source()
        data.add((S, Q, good))
        result = validator(data, shacl_graph=shapes("sh:datatype xsd:boolean"))
        assert result[0] is not bad_first
        if bad_first:
            assert next(result[1].objects(None, SH.value)) is bad


@pytest.mark.parametrize(
    "constraint",
    [
        "sh:node [sh:datatype xsd:boolean]",
        "sh:qualifiedValueShape [sh:datatype xsd:boolean];sh:qualifiedMinCount 1",
    ],
)
def test_sequence_nested_and_discarded_qualified_reports_keep_live_owner(constraint):
    value = Literal("none", datatype=XSD.boolean, normalize=True)
    data = Graph()
    data.add((S, Q, M))
    data.add((M, P, value))
    shape = shapes(constraint)
    expected = pyshacl.validate(data, shacl_graph=shape)
    actual = turbo.validate(data, shacl_graph=shape)
    assert expected[0] is False and actual[0] is False
    assert isomorphic(expected[1], actual[1])
    assert expected[2] == actual[2]
    for role in (SH.value, SH.focusNode):
        for reported in actual[1].objects(None, role):
            if isinstance(reported, Literal):
                assert reported is value


@pytest.mark.parametrize("kind", ["inactive", "no-focus"])
def test_unrequested_sequence_never_acquires_values(kind):
    class Source(Graph):
        def objects(self, subject=None, predicate=None, unique=False):
            raise AssertionError("An inactive sequence was acquired")

    for validator in (pyshacl.validate, turbo.validate):
        data = Source()
        data.add((S, Q, Literal(False)))
        options = {"focus_nodes": ["urn:absent"]} if kind == "no-focus" else {}
        prefix = "sh:deactivated true;" if kind == "inactive" else ""
        assert validator(data, shacl_graph=shapes("sh:datatype xsd:boolean", prefix), **options)[0]


@pytest.mark.parametrize("initial_union", [False, True])
@pytest.mark.parametrize("bad_first", [False, True])
def test_named_dataset_sequence_uses_prepared_union_cache_winner(initial_union, bad_first):
    results = []
    for validator in (pyshacl.validate, turbo.validate):
        data = Dataset(default_union=initial_union)
        bad = Literal("none", datatype=XSD.boolean, normalize=True)
        good = Literal("false", datatype=XSD.boolean, normalize=False)
        data.graph(URIRef("urn:link")).add((S, Q, M))
        for name, value in zip(
            ("urn:first", "urn:second"), (bad, good) if bad_first else (good, bad)
        ):
            data.graph(URIRef(name)).add((M, P, value))
        result = validator(data, shacl_graph=shapes("sh:datatype xsd:boolean"))
        assert data.default_union is True
        if not result[0]:
            assert next(result[1].objects(None, SH.value)) is bad
        results.append(result)
    assert results[0][0] is results[1][0]
    assert isomorphic(results[0][1], results[1][1])
    assert results[0][2] == results[1][2]
