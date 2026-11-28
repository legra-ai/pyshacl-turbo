"""Start-up import alias: ``import pyshacl`` resolves to pyshacl-turbo (ADR 0049).

The wheel's ``pyshacl_turbo_alias.pth`` calls :func:`install` when the
interpreter processes site-packages. This module only imports the standard
library, so start-up stays negligible: rdflib and the engine load only when a
program actually imports ``pyshacl``.

The alias is on by default. ``PYSHACL_TURBO_ALIAS=0`` turns it off for this
package and ``TURBO_ALIAS=0`` turns it off for every turbo package. The switch
is read on every lookup, so setting it before the first ``import pyshacl`` is
enough, including inside a running process.
"""

from __future__ import annotations

import importlib
import importlib.machinery
import importlib.util
import os
import sys

# Typing-only imports: collections.abc alone would double the hook's start-up cost.
TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from types import CodeType, ModuleType

SHARED_SWITCH = "TURBO_ALIAS"
"""Environment variable that turns off the import alias of every turbo package."""

OFF_VALUES = frozenset({"0", "false", "no", "off"})
"""Case-insensitive switch values that turn an alias off; any other value keeps it on."""


class TurboAliasError(ImportError):
    """A module of the aliased package that the turbo compatibility package does not provide."""

    def __init__(self, alias: TurboAlias, fullname: str) -> None:
        super().__init__(
            f"{fullname} is not provided by {alias.distribution}, which aliases "
            f"'{alias.name}' to '{alias.target}'. Set {alias.switch}=0 (or "
            f"{SHARED_SWITCH}=0) to import the real {alias.name} distribution instead.",
            name=fullname,
        )


class TurboAlias:
    """One import-name alias from an upstream package to a turbo compatibility package.

    A plain class rather than a dataclass: the hook runs at every interpreter
    start-up, so it imports nothing beyond what ``site`` has already loaded.
    """

    __slots__ = ("distribution", "name", "switch", "target")

    def __init__(self, *, name: str, target: str, distribution: str, switch: str) -> None:
        self.name = name
        self.target = target
        self.distribution = distribution
        self.switch = switch

    def enabled(self, environ: Mapping[str, str]) -> bool:
        """False when this package's switch or the shared switch is off."""
        return not any(
            environ.get(variable, "").strip().lower() in OFF_VALUES
            for variable in (self.switch, SHARED_SWITCH)
        )

    def target_name(self, fullname: str) -> str | None:
        if fullname == self.name:
            return self.target
        if fullname.startswith(self.name + "."):
            return self.target + fullname[len(self.name) :]
        return None


class AliasLoader:
    """Bind the aliased name to the already-imported compatibility module object."""

    def __init__(self, target: str) -> None:
        self.target = target

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> ModuleType:
        return importlib.import_module(self.target)

    def exec_module(self, module: ModuleType) -> None:
        # The compatibility module executed once under its own name; the alias
        # is the same object, so identity and isinstance checks agree.
        return None

    def get_code(self, fullname: str) -> CodeType | None:
        """Serve ``python -m pyshacl`` and ``-m pyshacl.cli`` from the target's code."""
        spec = importlib.util.find_spec(self.target)
        return spec.loader.get_code(self.target)


class AliasFinder:
    """A ``sys.meta_path`` finder placed ahead of the path finder."""

    def __init__(self, alias: TurboAlias, environ: Mapping[str, str] = os.environ) -> None:
        self.alias = alias
        self.environ = environ

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        target_name = self.alias.target_name(fullname)
        if target_name is None or not self.alias.enabled(self.environ):
            return None
        found = importlib.util.find_spec(target_name)
        if found is None:
            raise TurboAliasError(self.alias, fullname)
        return importlib.machinery.ModuleSpec(
            fullname,
            AliasLoader(target_name),
            is_package=found.submodule_search_locations is not None,
        )


PYSHACL = TurboAlias(
    name="pyshacl",
    target="pyshacl_turbo.compat",
    distribution="pyshacl-turbo",
    switch="PYSHACL_TURBO_ALIAS",
)


def install(meta_path: list[object] | None = None) -> AliasFinder:
    """Register the ``pyshacl`` alias once, ahead of every other finder."""
    finders = sys.meta_path if meta_path is None else meta_path
    for finder in finders:
        if isinstance(finder, AliasFinder) and finder.alias is PYSHACL:
            return finder
    finder = AliasFinder(PYSHACL)
    finders.insert(0, finder)
    return finder


def _command(module: str) -> None:
    # Resolved through the alias when it is on, and to the real pySHACL when it
    # is off, so the `pyshacl` commands always follow the switch.
    try:
        command = importlib.import_module(module)
    except ModuleNotFoundError as error:
        if error.name != PYSHACL.name and not (error.name or "").startswith(PYSHACL.name + "."):
            raise
        raise SystemExit(
            f"{PYSHACL.switch}=0 selects the real pyshacl distribution, which is not installed."
        ) from error
    command.main()


def validate_command() -> None:
    """The ``pyshacl`` console script."""
    _command("pyshacl.cli")


def rules_command() -> None:
    """The ``pyshacl_rules`` console script."""
    _command("pyshacl.cli_rules")
