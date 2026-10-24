"""Delegate native CI to the exact declared published provider's sole collector."""

import argparse
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def coverage_arguments(context):
    authority = context["receipt"]["provider"]
    owl = authority["peers"]["owlrl"]
    return SimpleNamespace(
        provider_source=context["owner"],
        provider_revision=None,
        source_archive=Path(authority["source_archive"]),
        source_sha256=authority["source_sha256"],
        collector_sha256=authority["collector_sha256"],
        facade_source=context["acceptance"],
        facade_wheel=context["wheel"],
        shacl_candidate_receipt=None,
        shacl_base_revision=None,
        owlrl_source=Path(owl["source"]),
        owlrl_archive=Path(owl["archive"]),
        owlrl_sha256=owl["sha256"],
        output=context["output"] / "native-coverage",
        python=sys.executable,
    )


def documentation(context):
    validation = load("provider_validation")
    compiler = load("owner_gates").compiler(context["owner"])
    validation.run(
        [
            "cargo",
            "+" + compiler,
            "doc",
            "--locked",
            "--no-deps",
            "--package",
            "pyshacl-turbo-engine",
            "--target-dir",
            context["output"] / "rustdoc",
        ],
        directory=context["owner"],
        env={**context["environment"], "RUSTUP_TOOLCHAIN": compiler, "RUSTDOCFLAGS": "-D warnings"},
    )


def execute(source, wheel, output, gate):
    if not sys.dont_write_bytecode:
        raise ValueError(
            "Native source verification requires python -B to preserve original inventories"
        )
    if gate not in {"coverage", "regex"}:
        raise ValueError("Unknown native owner lifecycle gate")
    validation = load("provider_validation")
    context = validation.prepare(source, wheel, output)
    if gate == "coverage":
        # The original archive inventory is checked before any compilation can
        # create generated files. The sole collector reattests its inputs too.
        load("provider_coverage").measure(coverage_arguments(context))
    load("owner_gates").execute(context, gate)
    if gate == "coverage":
        documentation(context)
    validation.verify_sources(context)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facade-source", type=Path, required=True)
    parser.add_argument("--facade-wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gate", choices=["coverage", "regex"], required=True)
    args = parser.parse_args()
    execute(args.facade_source, args.facade_wheel, args.output, args.gate)


if __name__ == "__main__":
    main()
