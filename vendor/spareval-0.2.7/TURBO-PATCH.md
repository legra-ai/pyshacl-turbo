# Local patches to spareval 0.2.7

Upstream Oxigraph revision: `0e81a29d27575ab69e7f85ea9c7f1058b277fcd0`.
MIT and Apache-2.0 license texts and original archive provenance are retained.

The prebinding patch supplies initially bound variables to the optimizer;
see `../sparql-prebinding.patch` and ADR 0004.

The opt-in `undefined-functions-as-expression-errors` feature changes only the
unregistered scalar-function arm in expression evaluator construction. An
unknown function returns an expression error (`None`) at evaluation time, so
FILTER, BIND, COALESCE and logical operators can handle it. Without this feature,
upstream's UnsupportedCustomFunction construction error remains unchanged.
Registered callbacks and unsupported aggregates are not changed by this patch.

The engine enables this feature for pySHACL compatibility under ADR 0012.
`tests/test_undefined_functions.py` checks the expression contexts, and
`test_sparql_function_error_cannot_become_a_conforming_report` keeps registered
callback failures visible.
