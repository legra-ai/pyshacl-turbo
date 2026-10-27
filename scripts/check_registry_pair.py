"""Block publication until the wheel's declared PyPI companion works natively."""

import argparse
import contextlib
import email
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from enum import StrEnum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from upstream_support.process_launch import install

INDEX = "https://pypi.org/simple"
BASE_PROBE = '''import json
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


class InstallationMode(StrEnum):
    """A registry publication check and an explicit original-wheel candidate differ."""

    REGISTRY = "registry"
    CANDIDATE = "candidate"


def installation_probe(mode, wheel=None, wheel_sha256=None):
    if not isinstance(mode, InstallationMode):
        raise TypeError("An explicit installation mode is required")
    if mode is InstallationMode.REGISTRY:
        if wheel is not None or wheel_sha256 is not None:
            raise ValueError("Registry mode cannot accept a candidate wheel")
        return """from importlib.metadata import distribution
if distribution("rdflib-turbo").read_text("direct_url.json") is not None:
    raise RuntimeError("Registry companion was installed from a direct URL")
"""
    if (
        wheel is None
        or not isinstance(wheel_sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", wheel_sha256)
    ):
        raise ValueError("An original native wheel and explicit SHA-256 are required")
    wheel = Path(wheel).resolve(strict=True)
    with wheel.open("rb") as original:
        if hashlib.file_digest(original, "sha256").hexdigest() != wheel_sha256:
            raise ValueError("Original native wheel SHA-256 mismatch")
    return f"""import hashlib, json
from importlib.metadata import distribution
from pathlib import Path
original = Path({str(wheel)!r})
with original.open("rb") as stream:
    actual_sha256 = hashlib.file_digest(stream, "sha256").hexdigest()
installed = json.loads(distribution("rdflib-turbo").read_text("direct_url.json") or "null")
if (actual_sha256 != {wheel_sha256!r} or not isinstance(installed, dict)
        or set(installed) != {{"url", "archive_info"}}
        or installed["url"] != {wheel.as_uri()!r}
        or not isinstance(installed["archive_info"], dict)):
    raise RuntimeError("Installed provider is not the exact original candidate wheel")
archive = installed["archive_info"]
if (set(archive) - {{"hashes", "hash"}}
        or ("hashes" in archive and archive["hashes"] != {{"sha256": {wheel_sha256!r}}})
        or ("hash" in archive and archive["hash"] != {("sha256=" + wheel_sha256)!r})):
    raise RuntimeError("Installed provider is not the exact original candidate wheel")
"""


def probe(mode, wheel=None, wheel_sha256=None):
    return installation_probe(mode, wheel, wheel_sha256) + BASE_PROBE


PROBE = probe(InstallationMode.REGISTRY)

RECEIPT_PROBE = """
import hashlib
from pathlib import Path

if provider.SHACL_ENGINE_SOURCE != "crates/engine":
    raise RuntimeError("Registry companion does not own the SHACL engine")
bindings = provider.shacl
if (canonical._native.CompiledShapes is not bindings.CompiledShapes
        or canonical._native.TargetData is not bindings.TargetData
        or bindings.SHACL_ENGINE_FINGERPRINT != fingerprint):
    raise RuntimeError("Facade classes do not belong to the registry native provider")

def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()

package = distribution("rdflib-turbo")
payload = {
    str(name): digest(Path(package.locate_file(name)))
    for name in package.files
    if str(name).startswith("rdflib_turbo/") and not str(name).endswith(".pyc")
}
native = Path(provider.__file__).resolve()
native_name = "rdflib_turbo/" + native.name
if native.suffix not in (".so", ".pyd") or payload.get(native_name) != digest(native):
    raise RuntimeError("Registry provider is not its installed native wheel payload")
print(json.dumps({"provider": package.version, "engine_source": provider.SHACL_ENGINE_SOURCE,
                  "fingerprint": fingerprint, "wheel_metadata": package.read_text("WHEEL"),
                  "payload": payload, "native_member": native_name}))
"""


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


def verify(wheel, *, receipt=False):
    wheel = Path(wheel).resolve(strict=True)
    requirement(wheel)
    install()
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("UV_", "PIP_", "PYTHON")) and key != "VIRTUAL_ENV"
    }
    environment.update(UV_NO_CONFIG="1", UV_NO_BUILD="1", UV_PYTHON=sys.executable)
    # ADR0006: change the parent directory instead of requesting fork-only cwd=.
    with (
        tempfile.TemporaryDirectory(prefix="pyshacl-registry-pair-") as temporary,
        contextlib.chdir(temporary),
    ):
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
            [
                *uv,
                "add",
                "--no-sync",
                "--refresh",
                "--extra",
                "test",
                "--default-index",
                INDEX,
                wheel,
            ],
            environment,
        )
        lock = tomllib.loads((project / "uv.lock").read_text())
        providers = [package for package in lock["package"] if package["name"] == "rdflib-turbo"]
        if len(providers) != 1 or providers[0].get("source") != {"registry": INDEX}:
            raise ValueError("The companion must resolve exclusively from the PyPI registry")
        run([*uv, "sync", "--locked", "--default-index", INDEX], environment)
        evidence = run(
            [
                *uv,
                "run",
                "--locked",
                "--no-sync",
                "python",
                "-I",
                "-c",
                PROBE + RECEIPT_PROBE if receipt else PROBE,
            ],
            environment,
        ).strip()
        if receipt:
            return json.loads(evidence.splitlines()[-1])
        print(evidence)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--receipt", action="store_true")
    arguments = parser.parse_args()
    result = verify(arguments.wheel, receipt=arguments.receipt)
    if arguments.receipt:
        print(json.dumps(result))
