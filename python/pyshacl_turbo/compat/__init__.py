"""The ``pyshacl`` import name, served by pyshacl-turbo (ADR 0049).

``import pyshacl`` resolves here through the start-up alias unless
``PYSHACL_TURBO_ALIAS=0`` or ``TURBO_ALIAS=0`` is set. ``pyshacl.__turbo__`` is
``True`` only on this package, so a program can always tell which engine it got.
"""

from importlib.metadata import version

from pyshacl_turbo import RuleExpandRunner, Shape, ShapesGraph, Validator
from pyshacl_turbo.compat.entrypoints import shacl_rules, validate, validate_each

PYSHACL_API_VERSION = "0.40.2"
"""The pinned pySHACL release whose public surface this package mirrors."""

__version__ = PYSHACL_API_VERSION
"""Version checks written against pySHACL compare with the mirrored API version."""

__turbo__ = True
"""Marker that ``pyshacl`` is served by pyshacl-turbo; the real pySHACL has no such attribute."""

__turbo_version__ = version("pyshacl-turbo")
"""The installed pyshacl-turbo version."""

__all__ = [
    "RuleExpandRunner",
    "Shape",
    "ShapesGraph",
    "Validator",
    "__version__",
    "shacl_rules",
    "validate",
    "validate_each",
]
