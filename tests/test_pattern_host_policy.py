"""Core pattern semantics follow the actual CPython host's character tables."""

import re

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SH


def fixture(pattern, value, flags=""):
    subject, predicate, shape = map(URIRef, ("urn:s", "urn:p", "urn:shape"))
    data = Graph().add((subject, predicate, Literal(value)))
    shapes = Graph()
    for triple in (
        (shape, SH.targetNode, subject),
        (shape, SH.path, predicate),
        (shape, SH.pattern, Literal(pattern)),
        (shape, SH.flags, Literal(flags)),
    ):
        shapes.add(triple)
    return data, shapes


@pytest.mark.parametrize(
    "pattern,value,flags",
    [
        (pattern, chr(codepoint), "")
        for pattern in (r"^\d$", r"^\w$", r"^[^\w]$", r"^\B.\B$")
        for codepoint in (0x1E5F1, 0x10D40, 0x11BF0, ord("5"))
    ]
    + [
        (r"^\w$", "\u1c89", ""),
        ("^\u1c89$", "\u1c8a", "i"),
        ("^[\u1c89]$", "\u1c8a", "i"),
        (r"^(.)\1$", "\u1c89\u1c8a", "i"),
        (r"^(?P<a>.)(?P=a)$", "\u1c89\u1c8a", "i"),
        (r"^(.)\1$", "i\u0131", "i"),
        (r"^(.)\1$", "s\u017f", "i"),
        (r"(?a:^\d$)", "\U0001e5f1", ""),
        (r"^\s$", "\x1c", ""),
        (r"\B", "", ""),
        (r"^\w$", "\u0345", "i"),
        (r"^[\w]$", "\u0345", "i"),
        (r"^[^\w]$", "\u0345", "i"),
        (r"^[\wA]$", "\u0345", "i"),
        (r"^[\wι]$", "\u0345", "i"),
        (r"^[\W]$", "\u0345", "i"),
    ],
)
def test_host_pattern_conformance_and_report(pattern, value, flags):
    data, shapes = fixture(pattern, value, flags)
    expected = pyshacl.validate(data, shacl_graph=shapes)
    actual = turbo.validate(data, shacl_graph=shapes)
    assert (
        actual[0] == expected[0] == bool(re.search(pattern, value, re.IGNORECASE if flags else 0))
    )
    assert actual[1].isomorphic(expected[1])
    assert actual[2] == expected[2]


@pytest.mark.parametrize("pattern", ["(?P<\u1c89>x)", r"\N{OL ONAL DIGIT ZERO}"])
def test_host_pattern_lexical_acceptance(pattern):
    data, shapes = fixture(pattern, "x")
    try:
        re.compile(pattern)
    except re.error:
        with pytest.raises(re.error):
            pyshacl.validate(data, shacl_graph=shapes)
        with pytest.raises(ValueError, match="Invalid sh:pattern"):
            turbo.validate(data, shacl_graph=shapes)
    else:
        expected = pyshacl.validate(data, shacl_graph=shapes)
        actual = turbo.validate(data, shacl_graph=shapes)
        assert actual[0] == expected[0]
        assert actual[1].isomorphic(expected[1])
        assert actual[2] == expected[2]
