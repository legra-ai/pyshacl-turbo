# Local Python regular-expression semantics

Published fancy-regex 0.19.2, with original revision and archive checksum in
`../rust-sources.json`. Its MIT license is retained. No upstream PR is submitted.

The opt-in `python-re` feature adds Python-compatible case-insensitive
backreferences and repeatable lookarounds. Backreferences compare simple
lowercase codepoints and advance by characters, so `i` can match `İ` despite
different UTF-8 byte lengths. The scoped `a` flag limits backreference case
matching to ASCII. The parser carries this mode through the AST to the VM.
With this feature disabled, existing matching behavior is retained; the added
AST field defaults to false in the retained upstream tests.

The SHACL engine separately translates Python character classes, flags and
anchors before compilation. This is not a general Python mode for unmodified
patterns passed directly to fancy-regex. Its seek optimization remains disabled:
the upstream case-folding approximation is not valid for Python backreferences.

Regressions are in `../../tests/test_patterns.py`.
