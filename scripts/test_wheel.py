"""Exercise uv environments, projects and tools with the exact release wheel."""

import contextlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from upstream_support.process_launch import install

PREFIXES = """@prefix ex: <urn:wheel:> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
"""


def run(arguments, environment, expected=0):
    result = subprocess.run(
        list(map(str, arguments)),
        env=environment,
        text=True,
        capture_output=True,
        check=False,
        timeout=180,
    )
    if result.returncode != expected:
        raise RuntimeError(
            f"{arguments!r}: expected exit {expected}, got {result.returncode}\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return result.stdout


def executable(directory, name):
    return directory / (name + ".exe" if sys.platform == "win32" else name)


def check_commands(validation, rules, directory, environment, version):
    assert run([*validation, "--version"], environment).strip() == version
    shapes = directory / "shapes.ttl"
    valid = run([*validation, directory / "valid.ttl", "-s", shapes], environment)
    assert "Conforms: True" in valid, valid
    invalid = run([*validation, directory / "invalid.ttl", "-s", shapes], environment, expected=1)
    assert "Conforms: False" in invalid and "MinCountConstraintComponent" in invalid, invalid
    expanded = run(
        [*rules, directory / "valid.ttl", "-s", directory / "rules.ttl", "-f", "nt"],
        environment,
    )
    derived = '<urn:wheel:s> <urn:wheel:derived> "true"^^<http://www.w3.org/2001/XMLSchema#boolean>'
    assert derived in expanded, expanded


def verify(directory):
    wheels = list(directory.resolve().glob("*.whl"))
    if len(wheels) != 1:
        raise ValueError(f"Expected one wheel, found {len(wheels)}")
    wheel = wheels[0]
    version = wheel.name.split("-")[1]
    install()
    with tempfile.TemporaryDirectory(prefix="pyshacl-turbo-wheel-") as temporary:
        directory = Path(temporary)
        tool_bin = directory / "tool-bin"
        environment = dict(os.environ)
        environment.pop("VIRTUAL_ENV", None)
        environment.pop("PYTHONPATH", None)
        environment.update(
            UV_CACHE_DIR=str(directory / "cache"),
            UV_TOOL_DIR=str(directory / "tools"),
            UV_TOOL_BIN_DIR=str(tool_bin),
            UV_PYTHON=sys.executable,
            UV_NO_BUILD="1",
            UV_NO_CONFIG="1",
        )
        (directory / "valid.ttl").write_text(PREFIXES + 'ex:s ex:p "value".')
        (directory / "invalid.ttl").write_text(PREFIXES + 'ex:s ex:other "value".')
        (directory / "shapes.ttl").write_text(
            PREFIXES + "ex:S sh:targetNode ex:s; sh:property [sh:path ex:p; sh:minCount 1]."
        )
        (directory / "rules.ttl").write_text(
            PREFIXES + "ex:S sh:targetNode ex:s; sh:rule [a sh:TripleRule; sh:subject sh:this; "
            "sh:predicate ex:derived; sh:object true]."
        )
        smoke = ROOT / "scripts/smoke_wheel.py"
        # Change the harness directory before launching: cwd= would require
        # unsafe fork on macOS. Every child still uses the guarded launcher.
        with contextlib.chdir(directory):
            venv = directory / "venv"
            run(["uv", "venv", "--python", sys.executable, venv], environment)
            bin_dir = venv / ("Scripts" if sys.platform == "win32" else "bin")
            python = executable(bin_dir, "python")
            run(["uv", "pip", "install", "--python", python, wheel], environment)
            run([python, "-I", smoke], environment)
            run([python, "-I", "-m", "pyshacl_turbo", "--help"], environment)
            check_commands(
                [executable(bin_dir, "pyshacl-turbo")],
                [executable(bin_dir, "pyshacl-turbo-rules")],
                directory,
                environment,
                version,
            )
            run(
                [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    python,
                    f"pyshacl-turbo[oxigraph] @ {wheel.as_uri()}",
                ],
                environment,
            )
            run([python, "-I", smoke, "--oxigraph"], environment)
            print(
                "uv venv / uv pip: API, both CLIs, exit codes and Store extra passed.", flush=True
            )

            project = directory / "project"
            run(["uv", "init", "--bare", "--vcs", "none", project], environment)
            run(["uv", "--directory", project, "add", wheel], environment)
            project_run = ["uv", "run", "--project", project, "--locked"]
            run([*project_run, "python", "-I", smoke], environment)
            check_commands(
                [*project_run, "pyshacl-turbo"],
                [*project_run, "pyshacl-turbo-rules"],
                directory,
                environment,
                version,
            )
            run(["uv", "--directory", project, "add", "--extra", "oxigraph", wheel], environment)
            run(["uv", "sync", "--project", project, "--locked"], environment)
            run([*project_run, "python", "-I", smoke, "--oxigraph"], environment)
            print(
                "uv add / uv sync / uv run: locked project, API, CLIs and Store extra passed.",
                flush=True,
            )

            check_commands(
                ["uvx", "--from", wheel, "pyshacl-turbo"],
                ["uvx", "--from", wheel, "pyshacl-turbo-rules"],
                directory,
                environment,
                version,
            )
            print("uvx: isolated validation and rules commands passed.", flush=True)

            run(["uv", "tool", "install", wheel], environment)
            check_commands(
                [executable(tool_bin, "pyshacl-turbo")],
                [executable(tool_bin, "pyshacl-turbo-rules")],
                directory,
                environment,
                version,
            )
            print("uv tool install: both installed commands passed.", flush=True)


if __name__ == "__main__":
    verify(Path(sys.argv[1]))
