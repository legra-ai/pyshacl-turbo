"""Sequence demand retains the actual path sets and selected Literal owners."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SH, XSD

S, P, Q = map(URIRef, ("urn:s", "urn:p", "urn:q"))


def shapes(predicates, constraint="sh:datatype xsd:boolean"):
    path = " ".join(f"<{p}>" for p in predicates)
    return Graph().parse(
        data="@prefix sh:<http://www.w3.org/ns/shacl#>. "
        "@prefix xsd:<http://www.w3.org/2001/XMLSchema#>. "
        f"<urn:S> sh:targetNode <urn:s>;sh:path ({path});{constraint}.",
        format="turtle",
    )


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize("length", [2, 3, 10, 11])
@pytest.mark.parametrize("assessment", ["invalid", "valid", "none"])
def test_sequence_owner_assessment_and_actual_depth_boundary(validator, length, assessment):
    selected = (
        Literal("none", datatype=XSD.boolean, normalize=True)
        if assessment == "invalid"
        else Literal(False)
        if assessment == "none"
        else Literal("false", datatype=XSD.boolean, normalize=False)
    )
    calls = []

    class Source(Graph):
        def objects(self, subject=None, predicate=None, unique=False):
            calls.append((str(subject), str(predicate)))
            return super().objects(subject, predicate, unique)

    data = Source()
    predicates = [URIRef(f"urn:p{i}") for i in range(length)]
    for i, predicate in enumerate(predicates):
        data.add(
            (
                S if i == 0 else URIRef(f"urn:s{i}"),
                predicate,
                selected if i + 1 == length else URIRef(f"urn:s{i + 1}"),
            )
        )
    expected_calls = [
        (str(S if i == 0 else URIRef(f"urn:s{i}")), str(p)) for i, p in enumerate(predicates[:10])
    ]
    if length == 11:
        error = (
            pyshacl.errors.ReportableRuntimeError
            if validator is pyshacl.validate
            else turbo.ReportableRuntimeError
        )
        with pytest.raises(error, match="^Path traversal depth is too much!$"):
            validator(data, shacl_graph=shapes(predicates))
    else:
        result = validator(data, shacl_graph=shapes(predicates))
        assert result[0] is (assessment != "invalid")
        if assessment == "invalid":
            assert next(result[1].objects(None, SH.value)) is selected
    assert calls == expected_calls


def test_sequence_depth_first_branch_order_and_exact_callback_failure():
    a, b = URIRef("urn:a"), URIRef("urn:b")
    middle = {a, b}
    expected_order = []
    first = next(iter(set(iter(middle))))
    failure = LookupError("actual first sequence branch", 62)
    outcomes = []

    def make_source(calls):
        class Source(Graph):
            def objects(self, subject=None, predicate=None, unique=False):
                calls.append((subject, predicate))
                if subject == S and predicate == Q:
                    return middle
                if predicate == P:
                    if subject == first:
                        return iter([URIRef("urn:next")])
                    raise AssertionError("A later branch ran before the first branch suffix")
                if predicate == URIRef("urn:r"):
                    raise failure
                return super().objects(subject, predicate, unique)

        return Source()

    for validator in (pyshacl.validate, turbo.validate):
        calls = []
        data = make_source(calls)
        data.add((S, Q, Literal(False)))
        with pytest.raises(LookupError) as observed:
            validator(data, shacl_graph=shapes([Q, P, URIRef("urn:r")]))
        assert observed.value is failure
        assert observed.value.args == ("actual first sequence branch", 62)
        assert observed.value.__context__ is None
        outcomes.append(calls)
    expected_order = [(S, Q), (first, P), (URIRef("urn:next"), URIRef("urn:r"))]
    assert outcomes == [expected_order, expected_order]


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize("kind", ["inherited", "getter", "set-copy", "high-b"])
def test_sequence_set_owners_deferred_errors_and_sparse_slots(validator, kind):
    events = []
    failure = ValueError("actual selected sequence cache", 92)

    class Selected(Literal):
        def __hash__(self):
            events.append("hash")
            return id(self) if kind == "high-b" else super().__hash__()

        @property
        def ill_typed(self):
            if kind == "getter":
                raise failure
            return super().ill_typed

    count = 64 if kind == "high-b" else 1
    selected = [
        Selected(
            "false" if kind != "inherited" else "none",
            datatype=XSD.boolean,
            normalize=kind == "inherited",
        )
        for _ in range(count)
    ]
    final = set(selected)
    subject = selected[0]

    class Source(Graph):
        def objects(self, focus=None, predicate=None, unique=False):
            if predicate == Q:
                return final if kind == "inherited" else iter([URIRef("urn:m")])
            if predicate == P:
                if kind == "inherited":
                    assert focus is subject
                return final
            return super().objects(focus, predicate, unique)

    data = Source()
    data.add((S, Q, Literal(False)))
    events.clear()
    if kind == "getter":
        with pytest.raises(ValueError) as observed:
            validator(data, shacl_graph=shapes([Q, P]))
        assert observed.value is failure
        assert observed.value.__context__ is None
    else:
        result = validator(data, shacl_graph=shapes([Q, P]))
        assert result[0] is (kind != "inherited")
        if kind == "inherited":
            assert next(result[1].objects(None, SH.value)) is subject
        # The Original DataGraph wrapper yields items before set construction;
        # each edge hashes them once, while update(existing_set) reuses hashes.
        if kind in {"set-copy", "high-b"}:
            assert events == ["hash"] * count
