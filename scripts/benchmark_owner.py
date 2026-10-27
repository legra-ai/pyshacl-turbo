"""Verify original provider archive authority before a release timing build."""

import email
import hashlib
import importlib.util
import re
import sys
import tomllib
import zipfile
from pathlib import Path


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_build_authority(args):
    if args.provider_source is not None or args.provider_revision is not None:
        raise ValueError(
            "Git-to-archive build equivalence is unsupported; provide the original sdist and SHA-256"
        )
    if args.provider_archive is None and args.provider_sha256 is None:
        return "registry"
    if (
        args.provider_archive is None
        or not isinstance(args.provider_sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", args.provider_sha256)
    ):
        raise ValueError("Both original provider sdist and mandatory SHA-256 are required")
    return "original-sdist"


def freeze_peer(source, revision, project, *, archive=None, sha256=None):
    if archive is not None or sha256 is not None:
        if revision is not None or archive is None or sha256 is None:
            raise ValueError("Choose exactly one complete original archive or Git peer authority")
        if project != "owlrl-turbo":
            raise ValueError("Original archive peer mode currently supports the OWL companion")
        files = load("provider_registry").verify_extracted(archive, source, sha256)
        if tomllib.loads((source / "pyproject.toml").read_text())["project"]["name"] != project:
            raise ValueError("Original peer archive has the wrong project identity")
        return {
            "kind": "original-sdist",
            "sha256": sha256,
            "filename": archive.name,
            "files": files,
        }
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Peer source requires its explicit immutable Git revision")
    frozen = load("provider_coverage").freeze_tree(source, project)
    if frozen["revision"] != revision:
        raise ValueError("Peer source differs from its explicit immutable Git revision")
    return {"kind": "git", **frozen}


def peer_authority(args, prefix, project):
    return freeze_peer(
        getattr(args, prefix + "_source"),
        getattr(args, prefix + "_revision"),
        project,
        archive=getattr(args, prefix + "_archive", None),
        sha256=getattr(args, prefix + "_archive_sha256", None),
    )


def verify_engine(source, record):
    if record["fingerprint"] != source["engine_fingerprint"]:
        raise ValueError("Built native wheel differs from its original archive engine fingerprint")


def verify_harness(source, frozen):
    if load("provider_coverage").freeze_tree(source, "pyshacl-turbo") != frozen:
        raise ValueError("Actual benchmark verification harness source changed")


def original_wheel(wheel, sha256):
    if (
        not isinstance(sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", sha256)
        or load("provider_validation").digest(wheel) != sha256
    ):
        raise ValueError("Original peer wheel differs from its mandatory SHA-256")


def pure_payload(source, wheel, project):
    package = project.replace("-", "_")
    manifest = tomllib.loads((source / "pyproject.toml").read_text())
    expected_version = manifest["project"]["version"]
    packages = manifest["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"]
    if (
        len(packages) != 1
        or Path(packages[0]).is_absolute()
        or ".." in Path(packages[0]).parts
        or Path(packages[0]).name != package
    ):
        raise ValueError("Pure peer requires its exact declared Hatch package path")
    with zipfile.ZipFile(wheel) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError("Original peer wheel has duplicate entries")
        names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(names) != 1:
            raise ValueError("Original peer wheel requires exactly one metadata record")
        metadata = email.message_from_bytes(archive.read(names[0]))
        wheel_metadata = email.message_from_bytes(
            archive.read(names[0].removesuffix("METADATA") + "WHEEL")
        )
        if (
            metadata["Name"] != project
            or metadata["Version"] != expected_version
            or wheel_metadata["Root-Is-Purelib"] != "true"
            or wheel_metadata.get_all("Tag") != ["py3-none-any"]
        ):
            raise ValueError("Original pure peer wheel does not match its source metadata")
        payload = {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist()
            if name.startswith(package + "/") and not name.endswith("/")
        }
    load("published_provider").verify_source_package(
        source, payload, None, package=package, source_root=source / packages[0]
    )
    return payload


def prepare(args, output):
    if not sys.dont_write_bytecode:
        raise ValueError("Archive-authority builds require python -B")
    kind = require_build_authority(args)
    peers = {}
    for project, prefix in (("pyshacl-turbo", "facade"), ("owlrl-turbo", "owlrl")):
        source, wheel = getattr(args, prefix + "_source"), getattr(args, prefix + "_wheel")
        original_wheel(wheel, getattr(args, prefix + "_wheel_sha256"))
        peers[prefix] = {
            "source": peer_authority(args, prefix, project),
            "wheel_sha256": getattr(args, prefix + "_wheel_sha256"),
            "payload": pure_payload(source, wheel, project),
        }
    if kind == "registry":
        authority = load("published_provider").resolve(
            args.facade_source, args.facade_wheel, output / "published-provider"
        )
        archive, sha256 = Path(authority["source_archive"]), authority["source_sha256"]
    else:
        archive, sha256 = args.provider_archive, args.provider_sha256
    registry = load("provider_registry")
    owner = registry.extract(archive, output / "owner", sha256)
    files = registry.verify_extracted(archive, owner, sha256)
    collector_path = owner / "scripts/native_coverage.py"
    collector_sha256 = load("provider_validation").digest(collector_path)
    # Verify the complete original inventory and local engine ownership with the
    # same authority helper used by the sole owner's coverage delegation.
    frozen = load("provider_coverage").verify_source(owner, None, collector_sha256, archive, sha256)
    resolved, profile = load("published_provider").metadata(owner)
    identity = load("provider_identity").derive(owner, resolved)
    spec = importlib.util.spec_from_file_location("original_owner_collector", collector_path)
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    facade = collector.freeze_facade_inputs(args.facade_source, args.facade_wheel)
    if (
        facade["revision"] != args.facade_revision
        or facade["package_payload"] != peers["facade"]["payload"]
    ):
        raise ValueError("Original owner collector did not bind the exact facade inputs")
    return {
        "owner": owner,
        "archive": archive,
        "collector": collector,
        "facade": facade,
        "receipt": {
            "build_authority": {"kind": kind, "archive_sha256": sha256, "files": files},
            "collector_sha256": collector_sha256,
            "source_identity": identity,
            "build_profile": profile,
            "peers": peers,
        },
        "frozen": frozen,
    }


def verify_inputs(args, context):
    receipt = context["receipt"]
    registry = load("provider_registry")
    files = registry.verify_extracted(
        context["archive"],
        context["owner"],
        receipt["build_authority"]["archive_sha256"],
        exact_inventory=False,
    )
    if files != receipt["build_authority"]["files"]:
        raise ValueError("Original provider source changed during its build")
    for project, prefix in (("pyshacl-turbo", "facade"), ("owlrl-turbo", "owlrl")):
        wheel = getattr(args, prefix + "_wheel")
        original_wheel(wheel, getattr(args, prefix + "_wheel_sha256"))
        if peer_authority(args, prefix, project) != receipt["peers"][prefix]["source"]:
            raise ValueError("Frozen peer inputs changed during the candidate build")
    context["collector"].verify_facade_inputs(
        args.facade_source, args.facade_wheel, context["facade"]
    )
