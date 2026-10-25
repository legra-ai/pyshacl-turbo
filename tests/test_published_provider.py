"""Published authority fails on actual capability before any native compilation."""

import hashlib
import importlib.util
import io
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest


def module():
    spec = importlib.util.spec_from_file_location(
        "published_provider", Path(__file__).resolve().parents[1] / "scripts/published_provider.py"
    )
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_incapable_registry_provider_stops_before_download_or_compilation(tmp_path, monkeypatch):
    helper = module()
    source = tmp_path / "facade"
    source.mkdir()
    (source / "pyproject.toml").write_text('[project]\ndependencies=["rdflib-turbo==0.2.0a9"]\n')
    wheel = tmp_path / "facade.whl"
    wheel.write_bytes(b"original")
    original = helper.load

    def unavailable(wheel, *, receipt):
        assert receipt is True
        raise RuntimeError("Registry provider has no native SHACL bindings")

    monkeypatch.setattr(
        helper,
        "load",
        lambda name: (
            SimpleNamespace(verify=unavailable) if name == "check_registry_pair" else original(name)
        ),
    )
    monkeypatch.setattr(helper.subprocess, "run", lambda *args, **kwargs: pytest.fail("compiled"))
    with pytest.raises(RuntimeError, match="no native SHACL bindings"):
        helper.resolve(source, wheel, tmp_path / "authority")
    assert (tmp_path / "authority/request.json").is_file()
    assert not (tmp_path / "authority/published-authority.json").exists()


def test_registry_wheel_payload_cannot_differ_from_installed_receipt(tmp_path):
    import zipfile

    wheel = tmp_path / "provider.whl"
    with zipfile.ZipFile(wheel, "w") as output:
        output.writestr("rdflib_turbo/_native.so", b"original")
    with pytest.raises(ValueError, match="installed registry payload"):
        module().verify_wheel(wheel, {"payload": {"rdflib_turbo/_native.so": "wrong"}})


def test_native_identity_is_derived_after_restoring_immutable_lock_peers(tmp_path, monkeypatch):
    helper = module()
    owner = tmp_path / "unpacked-native"
    owner.mkdir()
    data = b'[project]\nname="rdflib-turbo"\nversion="0.2.0a9"\n'
    (owner / "pyproject.toml").write_bytes(data)
    archive = tmp_path / "rdflib_turbo-0.2.0a9.tar.gz"
    with tarfile.open(archive, "w:gz") as output:
        member = tarfile.TarInfo("package/pyproject.toml")
        member.size = len(data)
        output.addfile(member, io.BytesIO(data))
    sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    destination = tmp_path / "cohort/rdflib-turbo"
    calls = []
    original = helper.load

    def restore(source, facade, output):
        calls.append("restore")
        destination.parent.mkdir()
        source.rename(destination)
        return {"provider_source": str(destination), "declaration_peer": {"version": "0.6.1"}}

    def metadata(source):
        assert source == destination
        calls.append("metadata")
        return {"source": str(source)}, {"profile": "original"}

    def derive(source, metadata):
        assert source == destination
        assert metadata["source"] == str(destination)
        calls.append("derive")
        return {"engine_fingerprint": "actual identity"}

    monkeypatch.setattr(helper, "metadata", metadata)
    monkeypatch.setattr(
        helper,
        "load",
        lambda name: (
            SimpleNamespace(
                restore=restore,
                verify_declaration_peer=lambda source, record, **kwargs: calls.append(
                    "verify-declaration"
                ),
            )
            if name == "published_peers"
            else SimpleNamespace(derive=derive)
            if name == "provider_identity"
            else original(name)
        ),
    )
    result = helper.restore_source_identity(
        owner, tmp_path / "current", tmp_path, archive, sha, "actual identity"
    )
    assert result["source"] == destination
    assert result["peers"]["declaration_peer"]["version"] == "0.6.1"
    assert calls == ["restore", "verify-declaration", "metadata", "derive", "verify-declaration"]


def test_source_metadata_selects_the_owners_compiler_without_a_facade_toolchain(
    tmp_path, monkeypatch
):
    helper = module()
    (tmp_path / "Cargo.toml").write_text(
        '[dependencies]\npyshacl-turbo-engine={path="crates/engine"}\n'
    )
    (tmp_path / "rust-toolchain.toml").write_text('[toolchain]\nchannel="1.99.1"\n')
    (tmp_path / "pyproject.toml").write_text(
        '[build-system]\nrequires=["maturin==1.15.0"]\n'
        '[tool.maturin]\nprofile="release"\nlocked=true\nfeatures=["pyo3/extension-module","persistence"]\n'
    )
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        if command[0] == "rustc":
            assert command == ["rustc", "+1.99.1", "-vV"]
            return SimpleNamespace(
                stdout="rustc 1.99.1 (fixture)\nhost: x86_64-unknown-linux-gnu\n"
            )
        assert command[:3] == ["cargo", "+1.99.1", "metadata"]
        assert command[command.index("--filter-platform") + 1] == "x86_64-unknown-linux-gnu"
        return SimpleNamespace(stdout='{"source":"fixture"}')

    monkeypatch.setattr(helper.subprocess, "run", run)
    metadata, _ = helper.metadata(tmp_path)
    assert metadata == {"source": "fixture"}
    assert len(calls) == 2
