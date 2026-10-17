"""Python regular-expression behavior is part of the pySHACL Core contract."""

import re

import pyshacl
import pyshacl_turbo as turbo
import pytest
from rdflib import BNode, Literal
from test_compatibility import EX, SH, compare, graph


def pattern_shapes(pattern, flags=""):
    shapes = graph("ex:P sh:targetNode ex:s; sh:path ex:p.")
    shapes.add((EX.P, SH.pattern, Literal(pattern)))
    if flags:
        shapes.add((EX.P, SH.flags, Literal(flags)))
    return shapes


@pytest.mark.parametrize(
    "pattern,flags,values",
    [
        pytest.param(r"(?a)^\d\s$", "", ["1 ", "١ ", "1\x1c"], id="ascii-digit-space"),
        pytest.param(r"(?i)^é$", "", ["É", "é", "E"], id="unicode-case-literal"),
        pytest.param(
            r"\A\x61\u0062\U00000063\N{LATIN SMALL LETTER D}\Z",
            "",
            ["abcd", "abcx"],
            id="unicode-escapes",
        ),
        pytest.param(r"^\00\077$", "", ["\0?", "?"], id="leading-zero-octal"),
        pytest.param(
            r"^(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)(k)(l)\12$",
            "",
            ["abcdefghijkll", "abcdefghijkl"],
            id="two-digit-backreference",
        ),
        pytest.param(r"foo(?=bar)", "", ["foobar", "foobaz"], id="lookahead"),
        pytest.param(r"foo(?!bar)", "", ["foobaz", "foobar"], id="negative-lookahead"),
        pytest.param(r"(?<=foo)bar", "", ["foobar", "bazbar"], id="lookbehind"),
        pytest.param(r"(?<!foo)bar", "", ["bazbar", "foobar"], id="negative-lookbehind"),
        pytest.param(r"^(\w+)-\1$", "", ["café-café", "a-b"], id="backreference"),
        pytest.param(
            r"^(?P<word>\w+)-(?P=word)$", "", ["same-same", "one-two"], id="named-backreference"
        ),
        pytest.param(r"^(a)?(?(1)b|c)$", "", ["ab", "c", "ac", "b"], id="conditional"),
        pytest.param(r"^(?>a|ab)c$", "", ["ac", "abc"], id="atomic-group"),
        pytest.param(r"^a*+a$", "", ["a", "aaa", "b"], id="possessive"),
        pytest.param(r"^abc$", "", ["abc", "abc\n", "abc\n\n", "xabc"], id="final-newline"),
        pytest.param(r"abc\Z", "", ["abc", "abc\n", "xabc"], id="absolute-end"),
        pytest.param(r"^abc$", "IM", ["ABC", "x\nABC\ny", "no"], id="uppercase-flags"),
        pytest.param(r"^a.b$", "s", ["a.b", "a\nb"], id="core-ignores-dotall-flag"),
        pytest.param(r"^a b$", "x", ["a b", "ab"], id="core-ignores-verbose-flag"),
        pytest.param(r"^abc$", "q!", ["abc", "ABC"], id="core-ignores-unknown-flags"),
        pytest.param(r"(?s)^a.b$", "", ["a\nb", "acb", "ab"], id="inline-dotall"),
        pytest.param("(?x)^ a # comment\n b $", "", ["ab", "a b"], id="inline-verbose"),
        pytest.param(r"(?m:^a$)(?-m:\n^b$)", "", ["a\nb", "b"], id="scoped-flags"),
        pytest.param(r"^\w+$", "", ["café", "²", "¼", "a\u0301", "\u200c"], id="unicode-word"),
        pytest.param(r"^\W+$", "", ["²", "¼", "\u0301", "\u200c"], id="unicode-nonword"),
        pytest.param(r"^\s$", "", ["\x1c", "\x1f", "\u0085", "x"], id="unicode-space"),
        pytest.param(r"^\S$", "", ["\x1c", "\x1f", "x"], id="unicode-nonspace"),
        pytest.param(r"\b²\b", "", ["²", "x²", "²\u0301"], id="unicode-boundary"),
        pytest.param(r"(?a)^\w+$", "", ["word_1", "café", "²"], id="ascii-mode"),
        pytest.param(r"(?a:\w+)-(?u:\w+)", "", ["abc-café", "é-é"], id="scoped-ascii"),
        pytest.param(r"^\v$", "", ["\v", "\n", "\r", "\f"], id="vertical-tab"),
        pytest.param(r"^\141$", "", ["a", "b"], id="octal"),
        pytest.param(r"^[\b]$", "", ["\b", "b"], id="class-backspace"),
        pytest.param(r"^[a&&b]$", "", ["a", "&", "b", "c"], id="literal-set-operators"),
        pytest.param(r"^[]a]$", "", ["]", "a", "b"], id="leading-closing-bracket"),
        pytest.param(r"a{,2}b", "", ["b", "ab", "aab", "c"], id="omitted-lower-bound"),
        pytest.param(r"a{b", "", ["a{b", "ab"], id="literal-brace"),
        pytest.param(r"^i$", "i", ["i", "I", "İ", "ı", "x"], id="unicode-casefold"),
        pytest.param(r"^[A-Z]+$", "i", ["İıſK", "abc", "é"], id="unicode-range-casefold"),
        pytest.param(r"(?ai)^i$", "", ["i", "I", "İ", "ı"], id="ascii-casefold"),
        pytest.param(r"(?ai)^é$", "", ["é", "É", "e"], id="ascii-casefold-nonascii"),
        pytest.param(r"(?ai)^[a-z]+$", "", ["abc", "ABC", "İ", "ı", "ſ", "K"], id="ascii-range"),
        pytest.param(r"(?ai)^[^a-z]$", "", ["a", "A", "İ", "ı", "ſ", "K"], id="ascii-negation"),
        pytest.param(r"^(?P<first>a)(b)\1\2$", "", ["abab", "aabb"], id="mixed-captures"),
        pytest.param(
            r"(?i)^(i)-\1$", "", ["i-İ", "İ-i", "ı-I", "i-I"], id="unicode-backref-casefold"
        ),
        pytest.param(r"(?ai)^(é)-\1$", "", ["é-é", "é-É"], id="ascii-backref-casefold"),
        pytest.param(r"^\N{LATIN SMALL LETTER E WITH ACUTE}$", "", ["é", "e"], id="unicode-name"),
        pytest.param(r"^\u0069$", "i", ["i", "I", "İ", "ı"], id="casefold-escaped-literal"),
        pytest.param(r"\B", "", ["", " ", "a", "ab", "²²"], id="non-boundary"),
        pytest.param(r"^[\w\W]$", "", ["x", "²", "\u0301", "\n"], id="class-complement"),
        pytest.param(r"^[\s\S]$", "", ["x", "\x1c", "\n"], id="space-complement"),
        pytest.param(r"^a{,}b$", "", ["b", "ab", "aaaab", "c"], id="unbounded-omitted-lower"),
        pytest.param(r"^a{,z}b$", "", ["a{,z}b", "ab"], id="literal-malformed-repeat"),
        pytest.param(r"(?x)^[ #\t\v]$", "", [" ", "#", "\t", "\v", "x"], id="verbose-class"),
        pytest.param(r"^(a)(?#ignore $ [ \) (?i)\1$", "", ["aa", "ab"], id="group-comment"),
        pytest.param(r"(?=a)*", "", ["a", "b", ""], id="repeated-assertion"),
        pytest.param(r"^[^\w\W]$", "", ["a", "²", " ", ""], id="empty-negated-class"),
        pytest.param(
            r"(?i)^(.)-\1$", "", ["s-ſ", "σ-ς", "k-K", "a-A", "ı-I"], id="backref-lowercase"
        ),
        pytest.param(r"(?ai)^(..)-\1$", "", ["éa-éA", "éa-ÉA"], id="mixed-ascii-backref"),
        pytest.param(r"^\<a\>$", "", ["<a>", "a", "<a"], id="escaped-punctuation"),
        pytest.param(r"(?ai)^\w$", "", ["a", "A", "İ", "ı", "ſ", "K"], id="ascii-word-ignorecase"),
        pytest.param(r"(?ai)\bK\b", "", ["K", "xK", " K "], id="ascii-boundary-ignorecase"),
        pytest.param(r"(?ai)^\é$", "", ["é", "É"], id="escaped-ascii-mode"),
    ],
)
def test_pattern_reports_match_python(pattern, flags, values):
    data = graph("")
    for value in values:
        data.add((EX.s, EX.p, Literal(value)))
    data.add((EX.s, EX.p, BNode("not-a-string")))
    shapes = pattern_shapes(pattern, flags)
    _, report, _ = compare(data, shapes)
    re_flags = (re.IGNORECASE if "i" in flags.lower() else 0) | (
        re.MULTILINE if "m" in flags.lower() else 0
    )
    matcher = re.compile(pattern, re_flags)
    expected_values = {Literal(value) for value in values if not matcher.search(value)}
    expected_values.add(BNode("not-a-string"))
    assert set(report.objects(None, SH.value)) == expected_values


@pytest.mark.parametrize(
    "pattern",
    [
        "(",
        "[",
        ")",
        "\\",
        "(?#unterminated",
        "(?au:a)",
        "(?P<unterminated",
        "[a-\\d]",
        "\\x",
        "\\u0",
        "\\U000000",
        "\\uZZZZ",
        "\\U00110000",
        "\\N",
        "\\N{UNKNOWN}",
        "\\N{unclosed",
        r"(?P<x>a)(?P<x>b)",
        r"\1",
        r"(?<=a+)b",
        r"\p{L}",
        r"(?<name>a)",
        r"a(?i)b",
        r"(?a-u:a)",
        r"[\w-a]",
        r"(?P<1>a)",
        r"(?R)",
        r"^*",
        r"$+",
        r"\b?",
        r"(?i-:a)",
        r"(?i-i:a)",
        r"(?u)(?a)a",
        r"(?a)(?u)a",
        r"(?(lookaround)a|b)",
    ],
)
def test_invalid_patterns_fail_before_inplace_rule_changes(pattern):
    shapes = pattern_shapes(pattern)
    shapes += graph("""ex:S sh:targetNode ex:s; sh:rule [a sh:TripleRule;
        sh:subject sh:this; sh:predicate ex:derived; sh:object true].""")
    for validate in (pyshacl.validate, turbo.validate):
        data = graph('ex:s ex:p "x".')
        before = set(data)
        with pytest.raises((re.error, ValueError)):
            validate(data, shacl_graph=shapes, advanced=True, inplace=True)
        # Turbo's documented success-only mutation contract is stronger than
        # pySHACL's: the reference can execute rules before loading a constraint.
        if validate is turbo.validate:
            assert set(data) == before


def test_compiled_patterns_reuse_without_cross_call_captures():
    shapes = pattern_shapes(r"^(?P<word>\w+)-(?P=word)$")
    program = turbo.compile_shapes(shapes)
    for value, conforms in [("same-same", True), ("one-two", False), ("next-next", True)]:
        data = graph("")
        data.add((EX.s, EX.p, Literal(value)))
        assert program.validate(data)[0] is conforms


def test_backtracking_limit_is_an_error_and_does_not_commit_rules():
    shapes = pattern_shapes(r"^(a|aa)+\1$")
    shapes += graph("""ex:S sh:targetNode ex:s; sh:rule [a sh:TripleRule;
        sh:subject sh:this; sh:predicate ex:derived; sh:object true].""")
    data = graph("")
    data.add((EX.s, EX.p, Literal("a" * 40 + "!")))
    before = set(data)
    with pytest.raises(RuntimeError, match="sh:pattern matching failed.*[Bb]acktrack"):
        turbo.validate(data, shacl_graph=shapes, advanced=True, inplace=True)
    assert set(data) == before


def test_pattern_on_iri_and_language_tagged_text():
    shapes = pattern_shapes(r"(?<=example\.com/)\w+$")
    data = graph("")
    for value in (EX.café, EX["not-a-word"], Literal("https://example.com/café", lang="fr")):
        data.add((EX.s, EX.p, value))
    compare(data, shapes)


def test_language_tagged_pattern_matches_reference():
    shapes = pattern_shapes("unused")
    shapes.set((EX.P, SH.pattern, Literal("abc", lang="en")))
    compare(graph('ex:s ex:p "abc", "no".'), shapes)
