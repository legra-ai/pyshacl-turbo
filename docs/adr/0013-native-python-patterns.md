# ADR 0013: Native Python regular-expression behavior for Core patterns

Status: Accepted

## Evidence

The Rust regex matcher rejected Python lookarounds, backreferences, conditionals
and atomic groups. It also differed on final newlines, word boundaries, Unicode
classes, flags and default result messages. These differences were outside the
403-case upstream inventory. Differential regressions reproduced them before
the implementation changed; they compare complete RDF reports and their values.

## Decision

Compile `sh:pattern` once into an immutable native program using fancy-regex
0.19.2. Translate Python syntax and lexical semantics in Rust, including Python
word/space classes, boundaries, strict end anchors, octal and Unicode escapes,
named characters, scoped flags and literal character-set operators. Match the
pinned pySHACL Core flag behavior: lowercase `sh:flags`, recognize `i` and `m`,
and ignore other letters. Inline Python flags remain effective. SPARQL REGEX
and REPLACE have separate semantics and are not changed by this decision.

Python uses a larger case closure for literals and character classes than for
backreferences. Handle literals and sets during translation. A documented,
opt-in `python-re` patch to fancy-regex compares backreferences by simple
lowercase codepoints, honors scoped ASCII mode, and advances by characters
instead of assuming matching UTF-8 byte lengths. It also accepts Python's
repeatable lookarounds. Preserve upstream behavior when the feature is disabled.
Retain the published sources, MIT license, source revision and archive checksum.
Keep its optional seek optimization disabled because its approximation assumes
the upstream case rules. No Python matcher, validator or reasoner is called.

Invalid patterns remain compilation errors. Matching uses the native engine's
backtracking limit; exhausting it is a hard execution error, never a violation
or a successful validation. Failed compilation or execution does not commit
rule or inference changes to caller-owned graphs. This retains ADR 0008's
compiled execution and success-only mutation contract.

## Verification and limits

The new 82-case regression suite covers complete reports, flags, Unicode and
ASCII modes, named/numbered/mixed captures, conditionals, repeated assertions,
atomic/possessive constructs, invalid syntax, language-tagged patterns, IRI
values, program reuse and backtracking errors. The patched dependency passes
303 upstream unit tests without default features and its full test suite with
default features (both with Python mode disabled). Two direct VM unit tests
verify Python backreference case rules, byte boundaries and mixed ASCII text.

This is bounded compatibility evidence against Python 3.11–3.13, not a claim
that every Python expression is equivalent. Unicode database versions, parser
resource limits, exact exception types and warning text are not fully aligned.
Python 3.14's new end-anchor and empty-input non-boundary behavior need a
separate version-aware contract. At this checkpoint SPARQL REGEX/REPLACE still
used Oxigraph's matcher; [ADR 0015](0015-native-sparql-patterns.md) subsequently
extends the native Python behavior to those functions. The strict upstream
inventory retains its one audited fixture failure.

See the [Python re reference](https://docs.python.org/3.13/library/re.html)
and the [dependency syntax](https://docs.rs/fancy-regex/0.19.2/fancy_regex/).
