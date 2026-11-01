"""Target-class discovery consumes actual source APIs and selected focus owners."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SH, XSD

C, D, P = map(URIRef, ("urn:C", "urn:D", "urn:p"))


def fixture(container, kind, events, failure):
    class Focus(URIRef):
        pass

    focus = (
        Literal("none", datatype=XSD.boolean, normalize=True)
        if kind == "literal-owner"
        else Focus("urn:focus")
    )
    bad = Literal("none", datatype=XSD.boolean, normalize=True)

    class Hooks:
        def subjects(self, predicate=None, object=None, unique=False):
            events.append(("subjects", predicate, object))
            if predicate == RDF.type and object == C:
                if kind == "error":
                    raise failure
                return iter(()) if kind == "subclass" else iter([focus])
            if predicate == RDF.type and object == D:
                return iter([focus])
            return super().subjects(predicate, object, unique)

        def transitive_subjects(self, predicate, object, remember=None):
            events.append(("transitive", predicate, object))
            if kind == "transitive-error":
                raise failure
            return iter([C, D]) if kind == "subclass" else iter([C])

        def objects(self, subject=None, predicate=None, unique=False):
            events.append(("objects", subject is focus))
            if predicate == P:
                assert subject is focus
                return iter([bad])
            return super().objects(subject, predicate, unique)

    base = Graph if container == "graph" else Dataset

    class Source(Hooks, base):
        pass

    data = Source() if container == "graph" else Source(default_union=container == "union")
    destination = data if container == "graph" else data.graph(URIRef("urn:named"))
    destination.add((URIRef("urn:raw"), P, Literal("ordinary") if kind == "m0" else bad))
    shape = Graph().parse(
        data="@prefix sh:<http://www.w3.org/ns/shacl#>. "
        "@prefix xsd:<http://www.w3.org/2001/XMLSchema#>. "
        "<urn:S> sh:targetClass <urn:C>;sh:path <urn:p>;sh:datatype xsd:boolean.",
        format="turtle",
    )
    events.clear()
    return data, shape, focus, bad


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize("container", ["graph", "default", "union"])
@pytest.mark.parametrize(
    "kind", ["owner", "literal-owner", "subclass", "error", "transitive-error", "m0"]
)
def test_target_class_actual_source_focus_owner_and_first_error(validator, container, kind):
    events = []
    failure = LookupError("actual target-class discovery", container, kind)
    data, shape, focus, bad = fixture(container, kind, events, failure)
    if kind in {"error", "transitive-error"}:
        with pytest.raises(LookupError) as observed:
            validator(data, shacl_graph=shape)
        assert observed.value is failure
        assert observed.value.args == ("actual target-class discovery", container, kind)
        assert observed.value.__context__ is None
    else:
        result = validator(data, shacl_graph=shape)
        assert result[0] is False
        assert len(result[1]) == 11
        reported_focus = next(result[1].objects(None, SH.focusNode))
        if isinstance(focus, Literal):
            assert reported_focus is focus
        else:
            assert type(reported_focus) is URIRef
            assert str(reported_focus) == str(focus)
        assert next(result[1].objects(None, SH.value)) is bad
    expected = [("subjects", RDF.type, C)]
    if kind != "error":
        expected.append(("transitive", RDFS.subClassOf, C))
    if kind == "subclass":
        expected.append(("subjects", RDF.type, D))
    if kind not in {"error", "transitive-error"}:
        expected.append(("objects", True))
    assert events == expected
    if container != "graph":
        assert data.default_union is True


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize(
    "kind", ["uri", "blank", "plain", "string", "integer", "boolean", "invalid", "unassessed"]
)
def test_target_class_node_datatype_does_not_apply_boolean_consumer_to_other_terms(validator, kind):
    from rdflib import BNode

    class GuardedURI(URIRef):
        @property
        def datatype(self):
            raise AssertionError("URI focus has no Literal datatype consumer")

    focus, datatype, expected = {
        "uri": (GuardedURI("urn:focus"), XSD.string, False),
        "blank": (BNode("focus"), XSD.string, False),
        "plain": (Literal("abc"), XSD.string, True),
        "string": (Literal("abc", datatype=XSD.string), XSD.string, True),
        "integer": (Literal(7), XSD.integer, True),
        "boolean": (Literal("false", datatype=XSD.boolean), XSD.boolean, True),
        "invalid": (Literal("none", datatype=XSD.boolean), XSD.boolean, False),
        "unassessed": (Literal(False), XSD.boolean, True),
    }[kind]

    class Source(Graph):
        def subjects(self, predicate=None, object=None, unique=False):
            if predicate == RDF.type and object == C:
                return iter([focus])
            return super().subjects(predicate, object, unique)

        def transitive_subjects(self, predicate, object, remember=None):
            return iter([object])

    data = Source()
    data.add((URIRef("urn:raw"), P, Literal("ordinary")))
    shapes = Graph()
    shape = URIRef("urn:S")
    shapes.add((shape, SH.targetClass, C))
    shapes.add((shape, SH.datatype, datatype))
    result = validator(data, shacl_graph=shapes)
    assert result[0] is expected
    assert len(result[1]) == (2 if expected else 10)
    if not expected and isinstance(focus, Literal):
        assert next(result[1].objects(None, SH.focusNode)) is focus
        assert next(result[1].objects(None, SH.value)) is focus


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize("filtered", [False, True])
def test_target_class_class_sensitive_focus_set_and_filter_keep_actual_subjects(
    validator, filtered
):
    class Focus(URIRef):
        pass

    base, derived = URIRef("urn:focus"), Focus("urn:focus")
    assert base != derived
    assert len({base, derived}) == 2
    calls = []

    class Source(Graph):
        def subjects(self, predicate=None, object=None, unique=False):
            if predicate == RDF.type and object == C:
                return iter([base, derived])
            return super().subjects(predicate, object, unique)

        def transitive_subjects(self, predicate, object, remember=None):
            return iter([object])

        def objects(self, subject=None, predicate=None, unique=False):
            if predicate == P:
                assert subject is base or subject is derived
                calls.append(subject)
                return iter(())
            return super().objects(subject, predicate, unique)

    data = Source()
    data.add((URIRef("urn:raw"), P, Literal("ordinary")))
    shapes = Graph().parse(
        data="@prefix sh:<http://www.w3.org/ns/shacl#>. <urn:S> sh:targetClass <urn:C>;sh:path <urn:p>;sh:minCount 1.",
        format="turtle",
    )
    options = {"focus_nodes": ["urn:focus"]} if filtered else {}
    result = validator(data, shacl_graph=shapes, **options)
    assert result[0] is False
    assert len(result[1]) == (10 if filtered else 18)
    if filtered:
        assert len(calls) == 1 and calls[0] is base
    else:
        assert len(calls) == 2
        assert any(node is base for node in calls)
        assert any(node is derived for node in calls)


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
def test_target_class_m0_child_property_keeps_inherited_focus_authority(validator):
    events = []
    data, _, _focus, bad = fixture("graph", "m0", events, LookupError("unused"))
    shapes = Graph().parse(
        data="@prefix sh:<http://www.w3.org/ns/shacl#>. @prefix xsd:<http://www.w3.org/2001/XMLSchema#>. <urn:S> sh:targetClass <urn:C>;sh:property <urn:Child>. <urn:Child> sh:path <urn:p>;sh:datatype xsd:boolean.",
        format="turtle",
    )
    result = validator(data, shacl_graph=shapes)
    assert result[0] is False
    assert len(result[1]) == 11
    assert next(result[1].objects(None, SH.value)) is bad
    assert events == [
        ("subjects", RDF.type, C),
        ("transitive", RDFS.subClassOf, C),
        ("objects", True),
    ]


@pytest.mark.parametrize("validator", [pyshacl.validate, turbo.validate])
@pytest.mark.parametrize("role", [SH.targetSubjectsOf, SH.targetObjectsOf])
@pytest.mark.parametrize("kind", ["long", "short", "iterator-error", "generator"])
def test_mixed_core_pair_targets_use_actual_two_item_unpacking(validator, role, kind):
    focus, other = URIRef("urn:focus"), URIRef("urn:other")
    failure = LookupError("actual source pair iterator")
    events = []
    pair = (focus, other) if role == SH.targetSubjectsOf else (other, focus)
    bad = Literal("none", datatype=XSD.boolean)

    class Row:
        def __iter__(self):
            events.append("row-iter")
            yield pair[0]
            raise failure

        def __getitem__(self, index):
            raise AssertionError("Source pair unpacking must use its iterator")

    class Source(Graph):
        def subjects(self, predicate=None, object=None, unique=False):
            if predicate == RDF.type and object == C:
                return iter(())
            return super().subjects(predicate, object, unique)

        def transitive_subjects(self, predicate, object, remember=None):
            return iter([object])

        def subject_objects(self, predicate=None, unique=False):
            if predicate == D:
                if kind == "long":
                    return iter([(*pair, other)])
                if kind == "short":
                    return iter([pair[:1]])
                if kind == "iterator-error":
                    return iter([Row()])
                return iter([iter(pair)])
            return super().subject_objects(predicate, unique)

        def objects(self, subject=None, predicate=None, unique=False):
            if predicate == P:
                assert subject is focus
                return iter([bad])
            return super().objects(subject, predicate, unique)

    data = Source()
    data.add((URIRef("urn:raw"), P, Literal("ordinary")))
    shapes = Graph()
    shape = URIRef("urn:S")
    for predicate, object in [
        (SH.targetClass, C),
        (role, D),
        (SH.path, P),
        (SH.datatype, XSD.boolean),
    ]:
        shapes.add((shape, predicate, object))
    if kind == "iterator-error":
        with pytest.raises(LookupError) as observed:
            validator(data, shacl_graph=shapes)
        assert observed.value is failure
        assert observed.value.__context__ is None
        assert events == ["row-iter"]
    elif kind in {"short", "long"}:
        with pytest.raises(ValueError) as observed:
            validator(data, shacl_graph=shapes)
        expected = (
            "not enough values to unpack (expected 2, got 1)"
            if kind == "short"
            else "too many values to unpack (expected 2)"
        )
        assert observed.value.args == (expected,)
    else:
        result = validator(data, shacl_graph=shapes)
        assert result[0] is False
        assert len(result[1]) == 11
        assert next(result[1].objects(None, SH.value)) is bad
