"""Block publication until the wheel's declared PyPI companion works natively."""

import argparse
import contextlib
import email
import os
import re
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from upstream_support.process_launch import install

INDEX = "https://pypi.org/simple"
PROBE = '''import json
from importlib.metadata import distribution, version
import pyshacl_turbo as canonical
import rdflib_turbo as runtime
from rdflib import URIRef
from rdflib.namespace import SH

provider = runtime._native
fingerprint = canonical._native.SHACL_ENGINE_FINGERPRINT
if not fingerprint or fingerprint != provider.SHACL_ENGINE_FINGERPRINT:
    raise RuntimeError("Registry companion has a different SHACL engine")
if provider.SHARED_SHACL_PROTOCOL != 1:
    raise RuntimeError("Registry companion does not implement protocol 1")
if distribution("rdflib-turbo").read_text("direct_url.json") is not None:
    raise RuntimeError("Registry companion was installed from a direct URL")

def forbid_conversion(*args, **kwargs):
    raise AssertionError("Registry Store validation must stay native")

runtime.Dataset.to_rdflib = forbid_conversion
program = canonical.compile_shapes("""@prefix sh: <http://www.w3.org/ns/shacl#> .
<urn:S> sh:targetNode <urn:s>; sh:property [sh:path <urn:p>; sh:minCount 1].""")
with runtime.Store() as store:
    store.update('INSERT DATA {<urn:s> <urn:seed> "present"}')
    conforms, report, _ = program.validate(store)
    if conforms:
        raise RuntimeError("Registry Store did not produce the expected violation")
    results = list(report.subjects(SH.focusNode, URIRef("urn:s")))
    if not results or not any((result, SH.resultPath, URIRef("urn:p")) in report for result in results):
        raise RuntimeError("Registry Store report lost the focus node or result path")
    with store.transaction() as transaction:
        transaction.update('INSERT DATA {<urn:s> <urn:p> "value"}')
        if not program.validate(transaction)[0]:
            raise RuntimeError("Registry transaction validation missed its pending write")
    if not program.validate(store)[0]:
        raise RuntimeError("Registry Store validation missed its committed write")
print(json.dumps({"canonical": version("pyshacl-turbo"),
                  "provider": version("rdflib-turbo"), "fingerprint": fingerprint}))
'''


def run(command, environment):
    result = subprocess.run(
        list(map(str, command)),
        env=environment,
        text=True,
        capture_output=True,
        check=False,
        timeout=180,
    )
    if result.returncode:
        raise RuntimeError(
            f"Registry pair command failed: {command!r}\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout


def requirement(wheel):
    with zipfile.ZipFile(wheel) as archive:
        metadata = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(metadata) != 1:
            raise ValueError("Expected exactly one wheel metadata entry")
        message = email.message_from_bytes(archive.read(metadata[0]))
    companions = [
        value
        for value in message.get_all("Requires-Dist", [])
        if re.match(r"rdflib[-_]turbo\b", value, re.IGNORECASE)
    ]
    if not companions or any("@" in value for value in companions):
        raise ValueError("The wheel must declare a registry requirement for rdflib-turbo")


def verify(wheel):
    wheel = Path(wheel).resolve(strict=True)
    requirement(wheel)
    install()
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("UV_", "PIP_", "PYTHON")) and key != "VIRTUAL_ENV"
    }
    environment.update(UV_NO_CONFIG="1", UV_NO_BUILD="1", UV_PYTHON=sys.executable)
    with tempfile.TemporaryDirectory(prefix="pyshacl-registry-pair-") as temporary:
        # ADR0006: change the parent directory instead of requesting fork-only cwd=.
        with contextlib.chdir(temporary):
            project = Path(temporary) / "project"
            run(
                ["uv", "--no-config", "init", "--bare", "--no-workspace", "--vcs", "none", project],
                environment,
            )
            run(
                ["uv", "--no-config", "python", "pin", "--project", project, sys.executable],
                environment,
            )
            uv = ["uv", "--no-config", "--directory", project]
            run(
                [*uv, "add", "--no-sync", "--extra", "test", "--default-index", INDEX, wheel],
                environment,
            )
            lock = tomllib.loads((project / "uv.lock").read_text())
            providers = [
                package for package in lock["package"] if package["name"] == "rdflib-turbo"
            ]
            if len(providers) != 1 or providers[0].get("source") != {"registry": INDEX}:
                raise ValueError("The companion must resolve exclusively from the PyPI registry")
            run([*uv, "sync", "--locked", "--default-index", INDEX], environment)
            print(
                run(
                    [*uv, "run", "--locked", "--no-sync", "python", "-I", "-c", PROBE], environment
                ).strip()
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    verify(parser.parse_args().wheel)
