"""Representative ``pyshacl`` / ``pyshacl_rules`` invocations compared with pySHACL (ADR 0049).

The reference runs as ``python -m pyshacl.cli`` with the import alias off. The
drop-in runs through the alias, both as ``python -m pyshacl`` and as the
installed console script. A case differs when the exit codes differ or when
exactly one side reports ``Conforms: True``/``False``; every differing case
must be listed in ``tests/divergences.toml`` under the ``pyshacl-cli`` suite.
"""

from __future__ import annotations

import enum
import os
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from upstream_support.process_launch import Popen

PREFIXES = "@prefix ex: <urn:cli:> .\n@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
FILES = {
    "valid.ttl": PREFIXES + 'ex:s ex:p "v" .\n',
    "invalid.ttl": PREFIXES + 'ex:s ex:q "v" .\n',
    "shapes.ttl": PREFIXES
    + "ex:S sh:targetNode ex:s; sh:property [sh:path ex:p; sh:minCount 1].\n",
    "rules.ttl": PREFIXES
    + "ex:S sh:targetNode ex:s; sh:rule [a sh:TripleRule; sh:subject sh:this; "
    "sh:predicate ex:d; sh:object true].\n",
    "bad.ttl": PREFIXES + "ex:a ex:b",
}


class Command(enum.StrEnum):
    """The two pySHACL commands and the modules that implement them."""

    VALIDATE = "pyshacl"
    RULES = "pyshacl_rules"

    @property
    def reference_module(self) -> str:
        return "pyshacl.cli" if self is Command.VALIDATE else "pyshacl.cli_rules"

    @property
    def alias_module(self) -> str:
        return "pyshacl" if self is Command.VALIDATE else "pyshacl.cli_rules"

    def script(self) -> Path:
        suffix = ".exe" if sys.platform == "win32" else ""
        return Path(sys.executable).parent / f"{self.value}{suffix}"


@dataclass(frozen=True)
class Outcome:
    """What the parity check compares: the exit code and the reported conformance."""

    code: int
    conforms: bool | None

    @classmethod
    def of(cls, code: int, stdout: str) -> Outcome:
        conforms = (
            True if "Conforms: True" in stdout else False if "Conforms: False" in stdout else None
        )
        return cls(code, conforms)


@dataclass(frozen=True)
class CliCase:
    """One invocation; file names in ``arguments`` resolve against the case directory."""

    case_id: str
    command: Command
    arguments: tuple[str, ...]
    environ: tuple[tuple[str, str], ...] = ()

    def argv(self, directory: Path) -> list[str]:
        return [str(directory / arg) if arg in FILES else arg for arg in self.arguments]

    def run(self, launcher: list[str], directory: Path, alias: bool) -> Outcome:
        env = {
            name: value
            for name, value in os.environ.items()
            if name not in {"PYSHACL_TURBO_ALIAS", "TURBO_ALIAS", "PYSHACL_SERVER", "PYSHACL_HTTP"}
        }
        env.update(self.environ)
        env["PYSHACL_TURBO_ALIAS"] = "1" if alias else "0"
        return run(launcher + self.argv(directory), env)

    def reference(self, directory: Path) -> Outcome:
        return self.run([sys.executable, "-m", self.command.reference_module], directory, False)

    def drop_in(self, directory: Path) -> tuple[Outcome, Outcome]:
        module = self.run([sys.executable, "-m", self.command.alias_module], directory, True)
        script = self.run([str(self.command.script())], directory, True)
        return module, script


def run(argv: list[str], env: Mapping[str, str]) -> Outcome:
    with Popen(
        argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=dict(env)
    ) as process:
        try:
            stdout, _ = process.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise
    return Outcome.of(process.returncode, stdout)


def write_files(directory: Path) -> None:
    for name, body in FILES.items():
        (directory / name).write_text(body, encoding="utf-8")


V, R = Command.VALIDATE, Command.RULES
CASES = (
    CliCase("validate/conforms", V, ("valid.ttl", "-s", "shapes.ttl")),
    CliCase("validate/violation", V, ("invalid.ttl", "-s", "shapes.ttl")),
    CliCase("validate/no-data", V, ()),
    CliCase("validate/missing-data-file", V, ("missing.ttl", "-s", "shapes.ttl")),
    CliCase("validate/bad-data-syntax", V, ("bad.ttl", "-s", "shapes.ttl")),
    CliCase("validate/bad-shapes-syntax", V, ("valid.ttl", "-s", "bad.ttl")),
    CliCase("validate/unknown-option", V, ("valid.ttl", "--bogus")),
    CliCase("validate/help", V, ("--help",)),
    CliCase("validate/version", V, ("--version",)),
    CliCase("validate/turtle-report", V, ("invalid.ttl", "-s", "shapes.ttl", "-f", "turtle")),
    CliCase("validate/table-report", V, ("invalid.ttl", "-s", "shapes.ttl", "-f", "table")),
    CliCase("validate/rdfs-inference", V, ("valid.ttl", "-s", "shapes.ttl", "-i", "rdfs")),
    CliCase("validate/unknown-inference", V, ("valid.ttl", "-s", "shapes.ttl", "-i", "bogus")),
    CliCase("validate/invalid-max-depth", V, ("valid.ttl", "-s", "shapes.ttl", "--max-depth", "x")),
    CliCase("validate/focus", V, ("invalid.ttl", "-s", "shapes.ttl", "--focus", "urn:cli:s")),
    CliCase("validate/allow-warnings", V, ("invalid.ttl", "-s", "shapes.ttl", "-w")),
    CliCase(
        "validate/validate-each",
        V,
        ("valid.ttl", "invalid.ttl", "-s", "shapes.ttl", "--validate-each"),
    ),
    CliCase("validate/sparql-mode-file", V, ("-q", "valid.ttl", "-s", "shapes.ttl")),
    CliCase("validate/sparql-mode-many", V, ("-q", "http://a", "http://b", "-s", "shapes.ttl")),
    CliCase("validate/server-option", V, ("--server",)),
    CliCase(
        "validate/server-environment",
        V,
        ("valid.ttl", "-s", "shapes.ttl"),
        (("PYSHACL_SERVER", "1"),),
    ),
    CliCase("validate/rules-option", V, ("--rules", "valid.ttl", "-s", "rules.ttl")),
    CliCase("rules/expand", R, ("valid.ttl", "-s", "rules.ttl")),
    CliCase("rules/expand-nt", R, ("valid.ttl", "-s", "rules.ttl", "-f", "nt")),
    CliCase("rules/no-data", R, ()),
    CliCase("rules/unknown-option", R, ("valid.ttl", "--bogus")),
    CliCase("rules/bad-shapes-syntax", R, ("valid.ttl", "-s", "bad.ttl")),
    CliCase("rules/version", R, ("--version",)),
)
