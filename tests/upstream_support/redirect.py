"""Test-only routing of the pinned upstream tests to turbo.

Reference report comparators remain test infrastructure. Original validation,
rules, loading and query-execution entry points cannot execute through this bridge.
"""

import importlib.util
import sys


def install():
    import pyshacl
    import pyshacl.rdfutil.load as loader
    import pyshacl.validator_conformance as conformance
    import pyshacl_turbo as turbo
    from pyshacl import entrypoints, errors, rdfutil

    if getattr(pyshacl, "_turbo_test_redirect", False):
        return

    def unsupported(name):
        def call(*args, **kwargs):
            raise NotImplementedError(f"Turbo compatibility entry point not implemented: {name}")

        return call

    for name in ("validate", "validate_each", "shacl_rules", "meta_validate"):
        implementation = getattr(turbo, name, unsupported(name))
        setattr(pyshacl, name, implementation)
        setattr(entrypoints, name, implementation)

    for name, implementation in (
        ("ValidationFailure", turbo.ValidationFailure),
        ("ReportableRuntimeError", turbo.ReportableRuntimeError),
        ("ConstraintLoadError", ValueError),
        ("ShapeLoadError", ValueError),
        ("RuleLoadError", ValueError),
    ):
        setattr(errors, name, implementation)
        if hasattr(conformance, name):
            setattr(conformance, name, implementation)

    implementation = getattr(turbo, "load_from_source", unsupported("load_from_source"))
    loader.load_from_source = implementation
    rdfutil.load_from_source = implementation
    for name in ("extract_query_and_expected_result", "evaluate_query_testcase"):
        setattr(conformance, name, getattr(turbo, name, unsupported(name)))

    from pyshacl.graph_abstraction import DataGraph
    from pyshacl.rule_expand_runner import RuleExpandRunner
    from pyshacl.validator import Validator

    DataGraph.from_oxigraph_store = staticmethod(
        getattr(turbo, "from_oxigraph_store", unsupported("from_oxigraph_store"))
    )
    Validator.run = unsupported("reference Validator.run is forbidden")
    RuleExpandRunner.run = unsupported("reference RuleExpandRunner.run is forbidden")
    pyshacl._turbo_test_redirect = True


def configure_item(item, redirect_cli=True):
    """Disable upstream failure allowances and route CLI subprocesses explicitly."""
    module = item.module
    for name in ("ALLOWABLE_FAILURES", "ALLOWABLE_NOT_IMPLEMENTED"):
        if hasattr(module, name):
            setattr(module, name, [])
    if not redirect_cli:
        return
    if hasattr(module, "pyshacl_command"):
        if importlib.util.find_spec("pyshacl_turbo.cli") is None:
            raise NotImplementedError("Turbo CLI is not implemented")
        module.pyshacl_command = [sys.executable, "-m", "pyshacl_turbo.cli"]
    if hasattr(module, "pyshacl_rules_command"):
        if importlib.util.find_spec("pyshacl_turbo.cli") is None:
            raise NotImplementedError("Turbo CLI is not implemented")
        module.pyshacl_rules_command = [sys.executable, "-m", "pyshacl_turbo.cli", "--rules"]
