"""Core numeric comparisons retain the caller's Decimal traps and flags."""

import decimal
import warnings

import pyshacl
import pyshacl_turbo
import pytest
from rdflib import Dataset as ReferenceDataset
from rdflib import Graph, Literal, Namespace
from rdflib.compare import to_canonical_graph
from rdflib.namespace import RDF, SH, XSD
from rdflib_turbo import StoreDataset

EX = Namespace("urn:decimal-comparison:")
RANGE_OPERATORS = ("minExclusive", "minInclusive", "maxExclusive", "maxInclusive")
PAIR_OPERATORS = ("lessThan", "lessThanOrEquals")
NUMERIC_WARNING = "NotImplemented should not be used in a boolean context"
FINITE_CASES = (
    "float-above-decimal",
    "float-below-decimal",
    "float-equal-decimal",
    "decimal-above-float",
    "decimal-below-float",
    "decimal-equal-float",
    "integer-equal-decimal",
)
SPECIAL_CASES = ("decimal-qnan", "decimal-snan", "float-qnan", "float-infinity", "decimal-infinity")
CONTEXT_CASES = (
    [(case, float_trap, True) for case in FINITE_CASES for float_trap in (False, True)]
    + [
        (case, float_trap, invalid_trap)
        for case in SPECIAL_CASES
        for float_trap in (False, True)
        for invalid_trap in (False, True)
    ]
    + [
        (case, False, True)
        for case in ("missing-decimal", "missing-left-decimal", "missing-right-decimal")
    ]
)


def numeric_literals(case):
    if case.startswith("float-"):
        value = (
            float("nan")
            if case == "float-qnan"
            else float("inf")
            if case == "float-infinity"
            else 1.0
        )
        bound = (
            decimal.Decimal(1)
            if case == "float-equal-decimal"
            else decimal.Decimal("1.1")
            if case == "float-below-decimal"
            else decimal.Decimal("0.9")
        )
        return Literal(value, datatype=XSD.double), Literal(bound, datatype=XSD.decimal)
    if case == "integer-equal-decimal":
        return Literal(1, datatype=XSD.integer), Literal(decimal.Decimal(1), datatype=XSD.decimal)
    if case == "missing-decimal":
        return Literal("invalid-decimal", datatype=XSD.decimal, normalize=False), Literal(
            1.0, datatype=XSD.double
        )
    if case in ("missing-left-decimal", "missing-right-decimal"):
        missing = Literal("invalid-decimal", datatype=XSD.decimal, normalize=False)
        valid = Literal(decimal.Decimal(1), datatype=XSD.decimal)
        return (missing, valid) if case == "missing-left-decimal" else (valid, missing)
    value = {
        "decimal-above-float": "1.1",
        "decimal-below-float": "0.9",
        "decimal-equal-float": "1",
        "decimal-qnan": "NaN",
        "decimal-snan": "sNaN",
        "decimal-infinity": "Infinity",
    }[case]
    return Literal(decimal.Decimal(value), datatype=XSD.decimal), Literal(1.0, datatype=XSD.double)


def term_state(term):
    if isinstance(term, Literal):
        return ("Literal", str(term), str(term.datatype) if term.datatype else None, term.language)
    return type(term).__name__, str(term)


def facts(graph, dataset=False):
    if dataset:
        default = graph.default_graph.identifier
        rows = [
            (*map(term_state, (s, p, o)), None if context == default else term_state(context))
            for s, p, o, context in graph.quads((None, None, None, None))
        ]
    else:
        rows = [tuple(map(term_state, row)) for row in graph]
    return sorted(rows, key=repr)


def observe(
    implementation,
    operator,
    case,
    route,
    float_trap,
    invalid_trap,
    *,
    initial_flags=(),
    compiled=None,
    prepared_shapes=None,
    warning_errors=False,
    raw_warnings=None,
):
    with decimal.localcontext() as context:
        context.traps[decimal.FloatOperation] = float_trap
        context.traps[decimal.InvalidOperation] = invalid_trap
        data = (
            (StoreDataset() if implementation is pyshacl_turbo else ReferenceDataset())
            if route == "dataset"
            else Graph()
        )
        graph = data.default_graph if route == "dataset" else data
        shapes = Graph()
        value, bound = numeric_literals(case)
        graph.add((EX.focus, EX.left, value))
        shapes.add((EX.shape, RDF.type, SH.PropertyShape))
        shapes.add((EX.shape, SH.targetNode, EX.focus))
        shapes.add((EX.shape, SH.path, EX.left))
        if operator in PAIR_OPERATORS:
            graph.add((EX.focus, EX.right, bound))
            shapes.add((EX.shape, SH[operator], EX.right))
        else:
            shapes.add((EX.shape, SH[operator], bound))
        if prepared_shapes is not None:
            shapes = Graph()
            for triple in prepared_shapes:
                shapes.add(triple)
        before_data, before_shapes = facts(data, route == "dataset"), facts(shapes)
        caches = [
            (
                type(term.value).__module__,
                type(term.value).__qualname__,
                repr(term.value),
                term.ill_typed,
            )
            for term in (value, bound)
        ]
        context.clear_flags()
        for flag in initial_flags:
            context.flags[flag] = True
        flags_before = sorted(signal.__name__ for signal, active in context.flags.items() if active)
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                if warning_errors:
                    warnings.filterwarnings(
                        "error",
                        message=NUMERIC_WARNING,
                        category=DeprecationWarning,
                    )
                try:
                    conforms, report, text = (
                        compiled.validate(data)
                        if compiled is not None
                        else implementation.validate(data, shacl_graph=shapes)
                    )
                except Exception as error:  # noqa: BLE001 - retain and compare every public exception.
                    outcome = {
                        "kind": "error",
                        "class": (type(error).__module__, type(error).__qualname__),
                        "args": repr(error.args),
                        "str": str(error),
                        "repr": repr(error),
                        "message": getattr(error, "message", None),
                        "link": getattr(error, "link", None),
                    }
                else:
                    outcome = {
                        "kind": "report",
                        "conforms": conforms,
                        "report": report,
                        "text": text,
                    }
            flags = sorted(signal.__name__ for signal, active in context.flags.items() if active)
            if raw_warnings is not None:
                raw_warnings.extend(
                    {
                        "category": (warning.category.__module__, warning.category.__qualname__),
                        "message": str(warning.message),
                        "filename": warning.filename,
                        "lineno": warning.lineno,
                        "operator": operator,
                    }
                    for warning in caught
                )
            after_data, after_shapes = facts(data, route == "dataset"), facts(shapes)
            if outcome["kind"] == "report":
                outcome["report"] = facts(to_canonical_graph(outcome["report"]))
            return {
                "before_data": before_data,
                "after_data": after_data,
                "before_shapes": before_shapes,
                "after_shapes": after_shapes,
                "caches": caches,
                "flags_before": flags_before,
                "flags": flags,
                "warnings": [
                    (
                        warning.category.__module__,
                        warning.category.__qualname__,
                        str(warning.message),
                        operator,
                    )
                    for warning in caught
                    if warning.category is DeprecationWarning
                    and str(warning.message) == NUMERIC_WARNING
                ],
                "outcome": outcome,
            }
        finally:
            if implementation is pyshacl_turbo and route == "dataset":
                data.close()


@pytest.mark.parametrize("route", ["graph", "dataset"])
@pytest.mark.parametrize("float_trap", [False, True])
def test_min_inclusive_current_standard_float_decimal_regression(route, float_trap):
    expected = observe(pyshacl, "minInclusive", "float-above-decimal", route, float_trap, True)
    actual = observe(pyshacl_turbo, "minInclusive", "float-above-decimal", route, float_trap, True)
    assert actual == expected


@pytest.mark.parametrize("route", ["graph", "dataset"])
@pytest.mark.parametrize("operator", (*RANGE_OPERATORS, *PAIR_OPERATORS))
@pytest.mark.parametrize("case,float_trap,invalid_trap", CONTEXT_CASES)
def test_core_numeric_comparisons_preserve_host_context(
    operator, case, route, float_trap, invalid_trap
):
    expected = observe(pyshacl, operator, case, route, float_trap, invalid_trap)
    actual = observe(pyshacl_turbo, operator, case, route, float_trap, invalid_trap)
    assert actual == expected


@pytest.mark.parametrize("route", ["graph", "dataset"])
@pytest.mark.parametrize("float_trap", [False, True])
def test_numeric_comparisons_preserve_existing_decimal_flags(route, float_trap):
    options = {"initial_flags": (decimal.Inexact,)}
    expected = observe(
        pyshacl, "minInclusive", "float-above-decimal", route, float_trap, True, **options
    )
    actual = observe(
        pyshacl_turbo, "minInclusive", "float-above-decimal", route, float_trap, True, **options
    )
    assert actual == expected


@pytest.mark.parametrize("route", ["graph", "dataset"])
def test_compiled_numeric_comparisons_capture_each_invocation_context(route):
    from pyshacl.shapes_graph import ShapesGraph as OriginalShapesGraph

    _, bound = numeric_literals("float-above-decimal")
    prepared = Graph()
    for triple in [
        (EX.shape, RDF.type, SH.PropertyShape),
        (EX.shape, SH.targetNode, EX.focus),
        (EX.shape, SH.path, EX.left),
        (EX.shape, SH.minInclusive, bound),
    ]:
        prepared.add(triple)
    OriginalShapesGraph(prepared)
    program = pyshacl_turbo.CompiledShapes(prepared)
    compiled_identity = program._native
    for float_trap in [False, True, False]:
        expected = observe(
            pyshacl,
            "minInclusive",
            "float-above-decimal",
            route,
            float_trap,
            True,
            prepared_shapes=prepared,
        )
        actual = observe(
            pyshacl_turbo,
            "minInclusive",
            "float-above-decimal",
            route,
            float_trap,
            True,
            compiled=program,
            prepared_shapes=prepared,
        )
        assert program._native is compiled_identity
        assert actual == expected


@pytest.mark.parametrize("route", ["graph", "dataset"])
@pytest.mark.parametrize("case", ["float-equal-decimal", "missing-right-decimal"])
@pytest.mark.parametrize("warning_errors", [False, True])
def test_numeric_pair_not_implemented_truth_uses_actual_host_warning_policy(
    route, case, warning_errors
):
    expected = observe(
        pyshacl, "lessThanOrEquals", case, route, True, True, warning_errors=warning_errors
    )
    actual = observe(
        pyshacl_turbo, "lessThanOrEquals", case, route, True, True, warning_errors=warning_errors
    )
    assert actual == expected
