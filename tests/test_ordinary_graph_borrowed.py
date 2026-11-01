"""Ordinary count validation must select values without transferring all DATA."""

import decimal
import gc
import weakref

import pytest
from pyshacl import validate as original_validate
from pyshacl_turbo import compile_shapes, validate
from rdflib import Graph, Literal, Namespace
from rdflib.collection import Collection
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, SH, XSD

EX = Namespace("urn:borrowed:")


class SelectedGraph(Graph):
    def __iter__(self):
        raise AssertionError("DATA iteration is forbidden")

    def serialize(self, *args, **kwargs):
        raise AssertionError("DATA serialization is forbidden")


@pytest.mark.parametrize("minimum", [1, 2])
def test_count_selects_ordinary_graph_without_bulk_transfer(minimum):
    data = SelectedGraph()
    data.add((EX.focus, EX.value, Literal("actual")))
    for index in range(128):
        data.add((EX[f"outside{index}"], EX.unselected, Literal(index)))
    shapes = Graph()
    shapes.add((EX.shape, SH.targetNode, EX.focus))
    shapes.add((EX.shape, SH.property, EX.property))
    shapes.add((EX.property, SH.path, EX.value))
    shapes.add((EX.property, SH.minCount, Literal(str(minimum), datatype=XSD.integer)))
    before = decimal.getcontext().copy()
    expected = original_validate(data, shacl_graph=shapes, inplace=True, advanced=False)
    actual = validate(data, shacl_graph=shapes, inplace=True, advanced=False)
    assert actual[0] is expected[0]
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
    assert dict(decimal.getcontext().flags) == dict(before.flags)
    assert decimal.getcontext().traps == before.traps


def test_selected_cursor_does_not_invent_iterator_close_callbacks():
    class Rows:
        def __init__(self, source, rows):
            self.source, self.rows = source, rows

        def __iter__(self):
            return self

        def __next__(self):
            return next(self.rows)

        def close(self):
            self.source.events.append("close")
            self.rows.close()

    class Source(SelectedGraph):
        def __init__(self):
            super().__init__()
            self.events = []

        def triples(self, pattern):
            return Rows(self, super().triples(pattern))

    shapes = Graph()
    shapes.add((EX.shape, SH.targetSubjectsOf, EX.target))
    shapes.add((EX.shape, SH.property, EX.property))
    shapes.add((EX.property, SH.path, EX.value))
    shapes.add((EX.property, SH.minCount, Literal("1", datatype=XSD.integer)))
    outcomes = []
    for operation in (original_validate, validate):
        data = Source()
        data.add((EX.focus, EX.target, EX.present))
        data.add((EX.focus, EX.value, Literal("actual")))
        result = operation(data, shacl_graph=shapes, inplace=True, advanced=False)
        outcomes.append((result, data.events))
    expected, actual = outcomes
    assert actual[1] == expected[1]
    assert actual[0][0] is expected[0][0]
    assert isomorphic(actual[0][1], expected[0][1])
    assert actual[0][2] == expected[0][2]


@pytest.mark.parametrize("focus", [EX.focus, Literal("actual focus")])
def test_class_target_count_failure_preserves_source_focus_presentation(focus):
    data = SelectedGraph()
    data.add((focus, RDF.type, EX.Class))
    shapes = Graph()
    shapes.add((EX.shape, SH.targetClass, EX.Class))
    shapes.add((EX.shape, SH.property, EX.property))
    shapes.add((EX.property, SH.path, EX.missing))
    shapes.add((EX.property, SH.minCount, Literal("1", datatype=XSD.integer)))
    expected = original_validate(data, shacl_graph=shapes, inplace=True, advanced=False)
    actual = validate(data, shacl_graph=shapes, inplace=True, advanced=False)
    assert actual[0] is expected[0] is False
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
    assert list(actual[1].objects(None, SH.focusNode)) == [focus]


@pytest.mark.parametrize("after_first", [False, True])
def test_cursor_preserves_first_source_error_and_context(after_first):
    class Failure(ValueError):
        pass

    class Source(SelectedGraph):
        def triples(self, pattern):
            if pattern[1] != EX.target:
                yield from super().triples(pattern)
                return
            try:
                if after_first:
                    yield from super().triples(pattern)
                decimal.getcontext().traps[decimal.InvalidOperation] = False
                decimal.getcontext().create_decimal("invalid")
                raise self.failure
            finally:
                self.events.append("finally")

    shapes = Graph()
    shapes.add((EX.shape, SH.targetSubjectsOf, EX.target))
    shapes.add((EX.shape, SH.property, EX.property))
    shapes.add((EX.property, SH.path, EX.value))
    shapes.add((EX.property, SH.minCount, Literal("1", datatype=XSD.integer)))
    observed = []
    for operation in (original_validate, validate):
        with decimal.localcontext() as context:
            context.clear_flags()
            source = Source()
            source.events, source.failure = [], Failure("actual source failure")
            source.add((EX.focus, EX.target, EX.present))
            with pytest.raises(Failure) as caught:
                operation(source, shacl_graph=shapes, inplace=True, advanced=False)
            assert caught.value is source.failure
            observed.append((source.events, context.copy()))
    expected, actual = observed
    assert actual[0] == expected[0]
    assert actual[1].flags == expected[1].flags
    assert dict(actual[1].flags) == dict(expected[1].flags)
    assert actual[1].traps == expected[1].traps


def test_source_cursor_owns_iterator_through_reentrant_collection():
    class Rows:
        def __init__(self, source, rows):
            self.rows = rows
            source.live.add(self)

        def __iter__(self):
            return self

        def __next__(self):
            gc.collect()
            return next(self.rows)

    class Source(SelectedGraph):
        def __init__(self):
            super().__init__()
            self.live = weakref.WeakSet()

        def triples(self, pattern):
            return Rows(self, super().triples(pattern))

    shapes = Graph()
    shapes.add((EX.shape, SH.targetSubjectsOf, EX.target))
    shapes.add((EX.shape, SH.property, EX.property))
    shapes.add((EX.property, SH.path, EX.value))
    shapes.add((EX.property, SH.minCount, Literal("1", datatype=XSD.integer)))
    results = []
    for operation in (original_validate, validate):
        source = Source()
        source.add((EX.focus, EX.target, EX.present))
        source.add((EX.focus, EX.value, Literal("actual")))
        results.append(operation(source, shacl_graph=shapes, inplace=True, advanced=False))
        gc.collect()
        assert not source.live
    assert results[0][0] is results[1][0]
    assert isomorphic(results[0][1], results[1][1])
    assert results[0][2] == results[1][2]


@pytest.mark.parametrize("component", [SH["class"], SH.closed, SH.sparql])
def test_indexed_program_rejects_foreign_borrowed_representation(component):
    from pyshacl_turbo import _native
    from pyshacl_turbo.graph_abstraction import DataGraph
    from rdflib import BNode, URIRef

    shapes = Graph()
    shapes.add((EX.shape, SH.targetNode, EX.focus))
    if component == SH.sparql:
        query = BNode()
        shapes.add((EX.shape, component, query))
        shapes.add((query, SH.select, Literal("SELECT $this WHERE { FILTER(false) }")))
    else:
        shapes.add((EX.shape, component, EX.Class if component == SH["class"] else Literal(True)))
    program = compile_shapes(shapes)
    assert program._native.selected_frames_only is False
    source = SelectedGraph()
    view = DataGraph.from_rdflib_graph(source)
    borrowed = _native.BooleanInput(
        source, {}, _terms=(URIRef, BNode, Literal), _dataset=None, _view=view
    )
    with pytest.raises(ValueError, match="Program requires indexed DATA validation"):
        program._native.validate(
            borrowed,
            "terms",
            None,
            False,
            100,
            15,
            False,
            False,
            False,
            False,
            [],
            [],
            [],
            _comparison_policy=_native._VALUE_COMPARISON_POLICY,
        )


@pytest.mark.parametrize(
    "component,bound", [(SH.minCount, 1), (SH.minCount, 2), (SH.maxCount, 1), (SH.maxCount, 0)]
)
@pytest.mark.parametrize("guarded", [False, True])
def test_count_does_not_inspect_selected_literal_metadata(component, bound, guarded):
    class CountLiteral(Literal):
        @property
        def datatype(self):
            raise AssertionError("Count must not read DATA datatype")

        @property
        def language(self):
            raise AssertionError("Count must not read DATA language")

    literal = (CountLiteral if guarded else Literal)("x" * (1024 * 1024), normalize=False)
    source = SelectedGraph()
    source.add((EX.focus, EX.value, literal))
    shapes = Graph()
    shapes.add((EX.shape, SH.targetNode, EX.focus))
    shapes.add((EX.shape, SH.property, EX.property))
    shapes.add((EX.property, SH.path, EX.value))
    shapes.add((EX.property, component, Literal(str(bound), datatype=XSD.integer)))
    expected = original_validate(source, shacl_graph=shapes, inplace=True, advanced=False)
    actual = validate(source, shacl_graph=shapes, inplace=True, advanced=False)
    assert actual[0] is expected[0]
    assert isomorphic(actual[1], expected[1])
    assert actual[2] == expected[2]
    assert not list(actual[1].objects(None, SH.value))


def test_count_sequence_preserves_actual_source_iterator_events():
    class Rows:
        def __init__(self, source, predicate, rows):
            self.source, self.predicate, self.rows = source, predicate, rows

        def __iter__(self):
            self.source.events.append(self.predicate)
            return self

        def __next__(self):
            return next(self.rows)

    class Source(SelectedGraph):
        def objects(self, subject=None, predicate=None, unique=False):
            return Rows(self, predicate, super().objects(subject, predicate, unique=unique))

    from rdflib import BNode

    shapes = Graph()
    path = BNode()
    Collection(shapes, path, [EX.first, EX.second])
    shapes.add((EX.shape, SH.targetNode, EX.focus))
    shapes.add((EX.shape, SH.property, EX.property))
    shapes.add((EX.property, SH.path, path))
    shapes.add((EX.property, SH.minCount, Literal("1", datatype=XSD.integer)))
    outcomes = []
    for operation in (original_validate, validate):
        source = Source()
        source.events = []
        source.add((EX.focus, EX.first, EX.middle))
        source.add((EX.middle, EX.second, Literal("actual")))
        result = operation(source, shacl_graph=shapes, inplace=True, advanced=False)
        outcomes.append((result, source.events))
    assert outcomes[0][1] == outcomes[1][1]
    assert outcomes[0][0][0] is outcomes[1][0][0]
    assert isomorphic(outcomes[0][0][1], outcomes[1][0][1])
    assert outcomes[0][0][2] == outcomes[1][0][2]


def test_count_retains_actual_sets_through_focus_batch_and_finalizer_status():
    class Ephemeral(Literal):
        def __del__(self):
            decimal.getcontext().create_decimal("invalid")

    class Source(SelectedGraph):
        def objects(self, subject=None, predicate=None, unique=False):
            if predicate != EX.value:
                yield from super().objects(subject, predicate, unique=unique)
                return
            if self.previous is not None:
                self.alive.append(self.previous() is not None)
            value = Ephemeral("actual", normalize=False)
            self.previous = weakref.ref(value)
            yield value

    shapes = Graph()
    shapes.add((EX.property, RDF.type, SH.PropertyShape))
    for focus in (EX.first, EX.second):
        shapes.add((EX.property, SH.targetNode, focus))
    shapes.add((EX.property, SH.path, EX.value))
    shapes.add((EX.property, SH.minCount, Literal("1", datatype=XSD.integer)))
    outcomes = []
    for operation in (original_validate, validate):
        with decimal.localcontext() as context:
            context.clear_flags()
            context.traps[decimal.InvalidOperation] = False
            source = Source()
            source.previous, source.alive = None, []
            result = operation(source, shacl_graph=shapes, inplace=True, advanced=False)
            assert source.previous() is None
            outcomes.append((result, source.alive, context.copy()))
    expected, actual = outcomes
    assert actual[1] == expected[1]
    assert actual[2].flags == expected[2].flags
    assert dict(actual[2].flags) == dict(expected[2].flags)
    assert actual[2].traps == expected[2].traps
    assert actual[0][0] is expected[0][0]
    assert isomorphic(actual[0][1], expected[0][1])
    assert actual[0][2] == expected[0][2]
