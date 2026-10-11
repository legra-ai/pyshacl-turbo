"""Run the locally corrected non-JS upstream suite, including parametrized cases."""

import argparse
import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", action="store_true")
    parser.add_argument("--output", type=Path)
    args, extra = parser.parse_known_args()
    source = ROOT / "vendor/pyshacl/test"
    files = []
    for path in sorted(source.rglob("*.py")):
        if "test_js" in path.parts or path.name == "test_108.py":
            continue
        nodes = ast.walk(ast.parse(path.read_text()))
        if any(isinstance(n, ast.FunctionDef) and n.name.startswith("test_") for n in nodes):
            files.append(str(path))
    report = args.output or ROOT / "docs" / (
        "upstream-reference.json" if args.reference else "upstream-coverage.json"
    )
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = sys.prefix
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    env["PYTHONPATH"] = os.pathsep.join(
        [str(ROOT / "tests/upstream_support"), str(source.parent), env.get("PYTHONPATH", "")]
    )
    env["PYSHACL_TURBO_UPSTREAM_REPORT"] = str(report.resolve())
    if args.reference:
        env.pop("PYSHACL_TURBO_TEST_REDIRECT", None)
    else:
        env["PYSHACL_TURBO_TEST_REDIRECT"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "upstream_plugin",
            "--continue-on-collection-errors",
            "--tb=short",
            "-q",
            "-W",
            "ignore::DeprecationWarning:rdflib",
            *files,
            *extra,
        ],
        check=False,
        cwd=source.parent,
        env=env,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
