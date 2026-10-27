"""Count and length parameters retain the reference's integer domains."""

import pyshacl
import pyshacl_turbo as turbo
import pytest
from pyshacl.errors import ConstraintLoadError
from rdflib import BNode, Literal
from rdflib.namespace import XSD
from test_compatibility import EX, SH, compare, graph

PARAMETERS = (
    "minCount",
    "maxCount",
    "minLength",
    "maxLength",
    "qualifiedMinCount",
    "qualifiedMaxCount",
)


def parameter_shape(parameter, value):
    shapes = graph("ex:S sh:targetNode ex:s; sh:path ex:p.")
    shapes.add((EX.S, SH[parameter], value))
    if parameter.startswith("qualified"):
        shapes.add((EX.S, SH.qualifiedValueShape, EX.ValueShape))
        shapes.add((EX.ValueShape, SH.nodeKind, SH.Literal))
    return shapes


@pytest.mark.parametrize("parameter", PARAMETERS)
@pytest.mark.parametrize("bound", [2**64, 2**64 + 1, 10**100])
def test_arbitrary_size_integer_parameters_match_reference(parameter, bound):
    data = graph('ex:s ex:p "abc".')
    shapes = parameter_shape(parameter, Literal(bound))
    compare(data, shapes)


@pytest.mark.parametrize("parameter", ["minLength", "maxLength"])
@pytest.mark.parametrize(
    "datatype",
    [
        XSD.integer,
        XSD.int,
        XSD.long,
        XSD.short,
        XSD.unsignedLong,
        XSD.unsignedInt,
        XSD.unsignedShort,
        XSD.unsignedByte,
        XSD.positiveInteger,
        XSD.nonNegativeInteger,
    ],
)
def test_length_parameters_accept_integer_datatypes(parameter, datatype):
    bound = 4 if parameter == "minLength" else 2
    shapes = parameter_shape(parameter, Literal(bound, datatype=datatype))
    assert not compare(graph('ex:s ex:p "abc".'), shapes)[0]


@pytest.mark.parametrize("parameter", ["qualifiedMinCount", "qualifiedMaxCount"])
@pytest.mark.parametrize(
    "value",
    [
        Literal(-1),
        Literal(-(10**100)),
        Literal(-1, datatype=XSD.negativeInteger),
        Literal(0, datatype=XSD.nonPositiveInteger),
        Literal(2, datatype=XSD.int),
        Literal(2, datatype=XSD.positiveInteger),
        Literal(True),
        Literal(False),
    ],
)
def test_qualified_counts_follow_reference_integer_value_rules(parameter, value):
    compare(graph('ex:s ex:p "abc".'), parameter_shape(parameter, value))


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("some_values", [False, True])
@pytest.mark.parametrize("disjoint", [False, True])
def test_qualified_counts_share_the_reference_empty_batch_shortcut(nested, some_values, disjoint):
    shapes = parameter_shape("qualifiedMaxCount", Literal(-1))
    shapes.add((EX.S, SH.qualifiedValueShapesDisjoint, Literal(disjoint)))
    data = graph('ex:other ex:p "abc".' if some_values else "")
    if nested:
        shapes.remove((EX.S, SH.targetNode, None))
        shapes += graph("ex:Parent sh:targetNode ex:root; sh:path ex:members; sh:property ex:S.")
        data += graph("ex:root ex:members ex:s, ex:other.")
    else:
        shapes.add((EX.S, SH.targetNode, EX.other))
    compare(data, shapes)


@pytest.mark.parametrize("parameter", PARAMETERS)
@pytest.mark.parametrize("lexical", ["  +0004\t", "1_0", "١٢"])
def test_integer_parameters_preserve_reference_lexical_forms(parameter, lexical):
    value = Literal(lexical, datatype=XSD.integer, normalize=False)
    compare(graph('ex:s ex:p "abc".'), parameter_shape(parameter, value))


@pytest.mark.parametrize("parameter", PARAMETERS)
@pytest.mark.parametrize("lexical", ["1__0", "_1", "1_", "1e2", "1.0", "", "no"])
def test_malformed_integer_lexical_forms_raise(parameter, lexical):
    value = Literal(lexical, datatype=XSD.integer, normalize=False)
    with pytest.raises((ConstraintLoadError, TypeError)) as expected:
        pyshacl.validate(graph('ex:s ex:p "abc".'), shacl_graph=parameter_shape(parameter, value))
    expected_type = TypeError if type(expected.value) is TypeError else turbo.ConstraintLoadError
    with pytest.raises(expected_type) as actual:
        turbo.validate(graph('ex:s ex:p "abc".'), shacl_graph=parameter_shape(parameter, value))
    assert str(actual.value) == str(expected.value)
    assert actual.value.args == expected.value.args
    if hasattr(expected.value, "link"):
        assert actual.value.link == expected.value.link


def test_zero_min_length_accepts_blank_nodes_like_reference():
    data = graph("")
    data.add((EX.s, EX.p, BNode("value")))
    assert compare(data, parameter_shape("minLength", Literal(0)))[0]


@pytest.mark.parametrize("parameter", ["minCount", "maxCount", "minLength", "maxLength"])
@pytest.mark.parametrize("value", [Literal(-1), Literal("no"), Literal("1", datatype=XSD.decimal)])
def test_invalid_integer_parameters_remain_hard_errors(parameter, value):
    for validate in (pyshacl.validate, turbo.validate):
        with pytest.raises((ConstraintLoadError, TypeError, ValueError)):
            validate(graph('ex:s ex:p "abc".'), shacl_graph=parameter_shape(parameter, value))


@pytest.mark.parametrize("parameter", ["minLength", "maxLength"])
@pytest.mark.parametrize("datatype", [XSD.negativeInteger, XSD.nonPositiveInteger, XSD.byte])
def test_length_parameters_reject_reference_excluded_datatypes(parameter, datatype):
    for validate in (pyshacl.validate, turbo.validate):
        with pytest.raises((ConstraintLoadError, ValueError)):
            validate(
                graph('ex:s ex:p "abc".'),
                shacl_graph=parameter_shape(parameter, Literal(0, datatype=datatype)),
            )
