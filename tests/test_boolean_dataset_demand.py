"""Readonly Dataset preparation uses the actual borrowed-view lifecycle."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.namespace import SH, XSD

S, P = URIRef("urn:s"), URIRef("urn:p")


def shapes(events, *, targets=False):
    class Shapes(Graph):
        def triples(self, pattern):
            if not any(event[0] == "shapes" for event in events):
                events.append(("shapes",))
            return super().triples(pattern)

    result = Shapes().parse(
        data="@prefix sh:<http://www.w3.org/ns/shacl#>. "
        "@prefix xsd:<http://www.w3.org/2001/XMLSchema#>. "
        f"<urn:S> sh:{'targetSubjectsOf <urn:p>' if targets else 'targetNode <urn:s>'};"
        "sh:path <urn:p>;sh:datatype xsd:boolean.",
        format="turtle",
    )
    events.clear()
    return result


def observed_dataset(events, initial, *, kind="ordinary", selected=None, failure=None):
    class Observed(Dataset):
        def __getattribute__(self, name):
            value = super().__getattribute__(name)
            if name == "default_union" and self.__dict__.get("armed", False):
                events.append(("getter", value))
                if kind == "getter-error":
                    raise failure
            return value

        def __setattr__(self, name, value):
            if name == "default_union" and self.__dict__.get("armed", False):
                events.append(("setter", value))
                writes = sum(event[0] == "setter" for event in events)
                if kind == "setter-first" or (kind == "setter-final" and writes == 4):
                    raise failure
                if kind == "setter-add" and value is True and not self.injected:
                    self.injected = True
                    self.graph(URIRef("urn:added")).add((S, P, selected))
                    events.append(("added",))
            super().__setattr__(name, value)

        def __len__(self):
            size = super().__len__()
            if self.__dict__.get("armed", False):
                events.append(("len", size))
                reads = sum(event[0] == "len" for event in events)
                if kind == "len-first" or (kind == "len-final" and reads == 4):
                    raise failure
            return size

        def objects(self, subject=None, predicate=None, unique=False):
            if subject == S and predicate == P:
                events.append(("objects", self.default_union, unique))
                if kind == "objects-error":
                    raise failure
                if kind == "iterator-error":

                    def rows():
                        yield selected
                        raise failure

                    return rows()
                if kind == "override":
                    return iter([selected])
            return super().objects(subject, predicate, unique)

        def quads(self, *args, **kwargs):
            if self.__dict__.get("armed", False):
                events.append(("raw",))
            return super().quads(*args, **kwargs)

    result = Observed(default_union=initial)
    result.injected = False
    return result


def prepare_prefix(events):
    stop = next((i for i, event in enumerate(events) if event[0] == "objects"), len(events))
    return [event for event in events[:stop] if event[0] not in {"raw", "added"}]


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize("initial", [False, True])
@pytest.mark.parametrize("bad_first", [False, True])
def test_named_only_dataset_preparation_and_selected_cache(validator, initial, bad_first):
    events = []
    good = Literal("false", datatype=XSD.boolean, normalize=False)
    bad = Literal("none", datatype=XSD.boolean, normalize=True)
    source = observed_dataset(events, initial)
    first, second = (bad, good) if bad_first else (good, bad)
    source.graph(URIRef("urn:first")).add((S, P, first))
    source.graph(URIRef("urn:second")).add((S, P, second))
    shape = shapes(events)
    source.armed = True
    result = validator(source, shacl_graph=shape)
    assert source.default_union is True
    assert result[0] is (not bad_first)
    assert len(result[1]) == (11 if bad_first else 2)
    if bad_first:
        assert next(result[1].objects(None, SH.value)) is first
    assert prepare_prefix(events) == [
        ("getter", initial),
        ("len", 1),
        ("setter", False),
        ("len", 1),
        ("setter", True),
        ("len", 1),
        ("setter", initial),
        ("shapes",),
        ("len", 1),
        ("setter", True),
        ("getter", True),
    ]
    assert [event for event in events if event[0] == "objects"] == [("objects", True, False)]
    if validator is turbo.validate:
        assert events.index(("raw",)) > max(
            i for i, event in enumerate(events) if event[0] == "setter"
        )


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize("initial", [False, True])
@pytest.mark.parametrize(
    "kind",
    [
        "getter-error",
        "setter-first",
        "setter-final",
        "len-first",
        "len-final",
        "objects-error",
        "iterator-error",
    ],
)
def test_dataset_preparation_and_objects_preserve_first_error(validator, initial, kind):
    events = []
    selected = Literal("none", datatype=XSD.boolean, normalize=True)
    failure = RuntimeError("actual Dataset preparation", kind)
    source = observed_dataset(events, initial, kind=kind, selected=selected, failure=failure)
    source.graph(URIRef("urn:named")).add((S, P, selected))
    shape = shapes(events)
    source.armed = True
    with pytest.raises(RuntimeError) as observed:
        validator(source, shacl_graph=shape)
    assert observed.value is failure
    assert observed.value.args == ("actual Dataset preparation", kind)
    assert observed.value.__context__ is None
    assert (
        not any(event[0] == "raw" for event in events)
        if kind not in {"objects-error", "iterator-error"}
        else True
    )


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize("initial", [False, True])
@pytest.mark.parametrize("kind", ["override", "setter-add"])
def test_dataset_live_selection_and_setter_fact_precede_capture(validator, initial, kind):
    events = []
    selected = Literal("none", datatype=XSD.boolean, normalize=True)
    source = observed_dataset(events, initial, kind=kind, selected=selected)
    source.graph(URIRef("urn:named")).add(
        (
            S,
            URIRef("urn:other") if kind == "setter-add" else P,
            Literal("false", datatype=XSD.boolean, normalize=False),
        )
    )
    shape = shapes(events, targets=kind == "setter-add")
    source.armed = True
    result = validator(source, shacl_graph=shape)
    assert result[0] is False
    assert len(result[1]) == 11
    assert next(result[1].objects(None, SH.value)) is selected
    assert source.default_union is True
    if kind == "setter-add":
        assert source.injected
        if validator is turbo.validate:
            assert events.index(("added",)) < events.index(("raw",))


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize("initial", [False, True])
def test_empty_dataset_preparation_preserves_actual_source_state(validator, initial):
    events = []
    source = observed_dataset(events, initial)
    shape = shapes(events)
    source.armed = True
    result = validator(source, shacl_graph=shape)
    assert result[0] is True and len(result[1]) == 2
    assert source.default_union is initial
    assert not any(event[0] == "setter" for event in events)
    # M0 remains the explicit lexical route; arbitrary overridden objects on an
    # input without candidate words is a separate, unclosed callback frontier.
    prefix = prepare_prefix(events)
    assert prefix[:5] == [("getter", initial), ("len", 0), ("len", 0), ("len", 0), ("shapes",)]
