"""Execute native verification only inside its independently attested provider."""

import importlib.util
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path


def compiler(owner):
    channel = tomllib.loads((owner / "rust-toolchain.toml").read_text())["toolchain"]["channel"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", channel):
        raise ValueError("Native gates require the owner's exact pinned compiler")
    return channel


def commands(owner, gate):
    cargo = ["cargo", "+" + compiler(owner)]
    uv = ["uv", "run", "--no-project", "--python", sys.executable, "python", "-m"]
    if gate == "regex":
        return [("regex", [*uv, "scripts.vendor_regex_tests"])]
    if gate != "coverage":
        raise ValueError("Unknown native owner gate")
    # bounded: the fixed native gate families preserved during ownership transfer.
    return [
        ("format", ["sh", "scripts/fmt.sh", "--check"]),
        (
            "clippy",
            [
                *cargo,
                "clippy",
                "--workspace",
                "--lib",
                "--tests",
                "--locked",
                "--",
                "-D",
                "warnings",
            ],
        ),
        ("metadata", ["make", "test-build-metadata"]),
        ("datatype", [*cargo, "test", "--locked", "-p", "oxsdatatypes", "--lib"]),
        ("evaluator", [*uv, "scripts.vendor_evaluator_tests"]),
        ("dataset", [*uv, "scripts.vendor_dataset_tests"]),
        ("storage", ["make", "test-store-contract"]),
        ("allocation", [*uv, "scripts.allocation_budgets"]),
    ]


def execute(context, gate):
    spec = importlib.util.spec_from_file_location(
        "provider_validation", Path(__file__).with_name("provider_validation.py")
    )
    validation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validation)
    owner, output = context["owner"], context["output"]
    selected = commands(owner, gate)
    expected = (
        ["scripts/vendor_regex_tests.py"]
        if gate == "regex"
        else [
            "scripts/fmt.sh",
            "scripts/vendor_evaluator_tests.py",
            "scripts/vendor_dataset_tests.py",
            "scripts/allocation_budgets.py",
            "tests/build-metadata/Cargo.toml",
            "tests/store-contract/Cargo.toml",
        ]
    )
    if any(not (owner / name).is_file() for name in expected):
        raise ValueError("Published native owner is missing mandatory verification inputs")
    authority = context["receipt"]["provider"]
    record = {
        "provider_source_sha256": authority["source_sha256"],
        "native_wheel_sha256": authority["native_wheel_sha256"],
        "engine_fingerprint": authority["identity"]["engine_fingerprint"],
        "gates": [],
    }
    receipt = output / f"native-owner-{gate}.json"
    env = {
        **context["environment"],
        "RUSTUP_TOOLCHAIN": compiler(owner),
        "PYO3_PYTHON": str(context["project"] / ".venv/bin/python"),
    }
    for name, command in selected:
        entry = {"name": name, "command": command, "status": "running"}
        record["gates"].append(entry)
        receipt.write_text(json.dumps(record, indent=2) + "\n")
        try:
            validation.run(command, directory=owner, env=env)
        except subprocess.CalledProcessError as error:
            entry.update(status="failed", returncode=error.returncode)
            receipt.write_text(json.dumps(record, indent=2) + "\n")
            raise
        entry.update(status="success", returncode=0)
        receipt.write_text(json.dumps(record, indent=2) + "\n")
