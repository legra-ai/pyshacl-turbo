"""Select the engine behind the upstream suite's own ``import pyshacl``.

The turbo run imports ``pyshacl`` through pyshacl-turbo's start-up alias (ADR
0049); the reference run turns the alias off and imports the pinned pySHACL.
Nothing is monkeypatched: the engine is whichever package ``import pyshacl``
resolves to, and that is verified before any test runs.
"""

import os
import sys
from enum import Enum

ENGINE_VARIABLE = "PYSHACL_TURBO_UPSTREAM_ENGINE"


class Engine(Enum):
    TURBO = "turbo"
    REFERENCE = "reference"

    @classmethod
    def requested(cls):
        return cls(os.environ[ENGINE_VARIABLE])

    @classmethod
    def imported(cls):
        import pyshacl

        return cls.TURBO if getattr(pyshacl, "__turbo__", False) is True else cls.REFERENCE


def require_engine():
    """Fail the session when ``import pyshacl`` resolves to the other engine."""
    requested, imported = Engine.requested(), Engine.imported()
    if requested is not imported:
        raise RuntimeError(
            f"The {requested.value} upstream run imported the {imported.value} pyshacl; "
            "check the pyshacl-turbo alias switch"
        )
    return requested


def configure_item(item, engine):
    """Disable upstream failure allowances and pin CLI subprocesses to the engine.

    The turbo run keeps the upstream commands, so the installed ``pyshacl`` and
    ``pyshacl_rules`` scripts run through the alias. The reference run uses the
    reference modules directly, because the last-installed script may be turbo's.
    """
    module = item.module
    for name in ("ALLOWABLE_FAILURES", "ALLOWABLE_NOT_IMPLEMENTED"):
        if hasattr(module, name):
            setattr(module, name, [])
    if engine is Engine.TURBO:
        return
    if hasattr(module, "pyshacl_command"):
        module.pyshacl_command = [sys.executable, "-m", "pyshacl.cli"]
    if hasattr(module, "pyshacl_rules_command"):
        module.pyshacl_rules_command = [sys.executable, "-m", "pyshacl.cli_rules"]
