"""Timing builds require original archive authority rather than inferred Git equivalence."""

import hashlib
import importlib.util
import io
import tarfile
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


def helper():
    spec = importlib.util.spec_from_file_location(
        "benchmark_owner", ROOT / "scripts/benchmark_owner.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_git_source_is_not_a_supported_archive_build_bridge(tmp_path):
    module = helper()
    args = SimpleNamespace(
        provider_source=tmp_path,
        provider_revision="a" * 40,
        provider_archive=None,
        provider_sha256=None,
    )
    with pytest.raises(ValueError, match="Git.*archive.*unsupported"):
        module.require_build_authority(args)


def test_explicit_original_provider_archive_requires_its_sha256(tmp_path):
    module = helper()
    args = SimpleNamespace(
        provider_source=None,
        provider_revision=None,
        provider_archive=tmp_path / "original.tar.gz",
        provider_sha256=None,
    )
    with pytest.raises(ValueError, match="original.*SHA-256"):
        module.require_build_authority(args)
    args.provider_sha256 = "a" * 64
    assert module.require_build_authority(args) == "original-sdist"
    args.provider_archive = None
    with pytest.raises(ValueError, match="original.*SHA-256"):
        module.require_build_authority(args)
    args.provider_sha256 = None
    assert module.require_build_authority(args) == "registry"


def test_peer_sources_need_exact_explicit_git_revisions_before_any_build(monkeypatch, tmp_path):
    module = helper()
    monkeypatch.setattr(
        module,
        "load",
        lambda name: pytest.fail("Invalid source revision reached an authority helper"),
    )
    with pytest.raises(ValueError, match="immutable.*revision"):
        module.freeze_peer(tmp_path, "main", "pyshacl-turbo")


def test_runtime_payload_mismatch_cannot_be_called_source_equivalent():
    module = helper()
    source = {"engine_fingerprint": "expected"}
    record = {"fingerprint": "different"}
    with pytest.raises(ValueError, match="archive.*fingerprint"):
        module.verify_engine(source, record)


def test_runtime_acceptance_source_does_not_substitute_for_actual_harness(monkeypatch, tmp_path):
    module = helper()
    expected = {"revision": "a" * 40, "files": {"scripts/benchmark_owner.py": "original"}}
    actual = {"revision": "a" * 40, "files": {"scripts/benchmark_owner.py": "changed"}}
    seen = []

    def freeze(source, project):
        seen.append((source, project))
        return actual

    monkeypatch.setattr(module, "load", lambda name: SimpleNamespace(freeze_tree=freeze))
    with pytest.raises(ValueError, match="harness source changed"):
        module.verify_harness(tmp_path / "actual-harness", expected)
    assert seen == [(tmp_path / "actual-harness", "pyshacl-turbo")]


def test_peer_payload_uses_its_declared_hatch_package_path(tmp_path):
    module = helper()
    source = tmp_path / "owl-source"
    package = source / "src/owlrl_turbo"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("VALUE = 1\n")
    (source / "pyproject.toml").write_text(
        '[project]\nname="owlrl-turbo"\nversion="0.1.0a3"\n[tool.hatch.build.targets.wheel]\npackages=["src/owlrl_turbo"]\n'
    )
    wheel = tmp_path / "original.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("owlrl_turbo/__init__.py", "VALUE = 1\n")
        archive.writestr(
            "owlrl_turbo-0.1.0a3.dist-info/METADATA", "Name: owlrl-turbo\nVersion: 0.1.0a3\n"
        )
        archive.writestr(
            "owlrl_turbo-0.1.0a3.dist-info/WHEEL", "Root-Is-Purelib: true\nTag: py3-none-any\n"
        )
    assert module.pure_payload(source, wheel, "owlrl-turbo")
    (package / "__init__.py").write_text("VALUE = 2\n")
    with pytest.raises(ValueError, match="source package differs"):
        module.pure_payload(source, wheel, "owlrl-turbo")


def test_owl_peer_original_archive_authority_is_disjoint_from_git(tmp_path):
    module = helper()
    source = tmp_path / "original-owl"
    source.mkdir()
    manifest = b'[project]\nname="owlrl-turbo"\nversion="0.1.0a3"\n'
    (source / "pyproject.toml").write_bytes(manifest)
    archive = tmp_path / "owlrl_turbo-0.1.0a3.tar.gz"
    with tarfile.open(archive, "w:gz") as package:
        member = tarfile.TarInfo("owlrl_turbo-0.1.0a3/pyproject.toml")
        member.size = len(manifest)
        package.addfile(member, io.BytesIO(manifest))
    sha256 = hashlib.sha256(archive.read_bytes()).hexdigest()
    authority = module.freeze_peer(source, None, "owlrl-turbo", archive=archive, sha256=sha256)
    assert authority["kind"] == "original-sdist"
    assert authority["sha256"] == sha256
    assert "revision" not in authority
    assert authority["files"] == {"pyproject.toml": hashlib.sha256(manifest).hexdigest()}
    with pytest.raises(ValueError, match="one.*authority"):
        module.freeze_peer(source, "a" * 40, "owlrl-turbo", archive=archive, sha256=sha256)
    (source / "pyproject.toml").write_bytes(manifest + b"# changed\n")
    with pytest.raises(ValueError, match="Source bytes differ"):
        module.freeze_peer(source, None, "owlrl-turbo", archive=archive, sha256=sha256)
