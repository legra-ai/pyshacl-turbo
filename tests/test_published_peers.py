"""Published native test peers come from exact lock entries and original archives."""

import hashlib
import importlib.util
import io
import shutil
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest


def helper():
    path = Path(__file__).resolve().parents[1] / "scripts/published_peers.py"
    spec = importlib.util.spec_from_file_location("published_peers", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def owner(tmp_path, *, path="../pyshacl-turbo", version="0.6.1"):
    source = tmp_path / "rdflib-turbo"
    source.mkdir()
    (source / "pyproject.toml").write_text(
        '[project]\nname="rdflib-turbo"\nversion="0.2.0a9"\n'
        f'[tool.uv.sources]\npyshacl-turbo={{path="{path}",editable=true}}\n'
    )
    (source / "uv.lock").write_text(
        f'[[package]]\nname="pyshacl-turbo"\nversion="{version}"\n'
        f'source={{editable="{path}"}}\n'
        '[[package]]\nname="owlrl-turbo"\nversion="0.1.0a3"\n'
        'source={registry="https://pypi.org/simple"}\n'
    )
    return source


def test_declaration_peer_uses_its_locked_version_not_current_facade(tmp_path):
    module = helper()
    source = owner(tmp_path)
    assert module.locked_version(source, "pyshacl-turbo") == "0.6.1"
    assert module.locked_version(source, "owlrl-turbo") == "0.1.0a3"
    assert module.adjacent_peer(source, "pyshacl-turbo") == "pyshacl-turbo"


@pytest.mark.parametrize(
    "path", ["../../escape", "/tmp/peer", "../other-project", "../pyshacl-turbo/extra"]
)
def test_original_source_peer_cannot_escape_the_declared_cohort(tmp_path, path):
    with pytest.raises(ValueError, match="adjacent"):
        helper().adjacent_peer(owner(tmp_path, path=path), "pyshacl-turbo")


def test_registry_peer_version_must_be_exact_and_unambiguous(tmp_path):
    source = owner(tmp_path, version="main")
    with pytest.raises(ValueError, match="exact locked"):
        helper().locked_version(source, "pyshacl-turbo")
    with (source / "uv.lock").open("a") as stream:
        stream.write('[[package]]\nname="owlrl-turbo"\nversion="0.1.0a4"\n')
    with pytest.raises(ValueError, match="one locked"):
        helper().locked_version(source, "owlrl-turbo")


@pytest.mark.parametrize("actual_version", ["0.6.1", "0.6.2"])
def test_original_peer_archive_metadata_must_match_locked_registry_identity(
    tmp_path, monkeypatch, actual_version
):
    module = helper()
    registry = module.load("provider_registry")
    archive = tmp_path / "pyshacl_turbo-0.6.1.tar.gz"
    data = f'[project]\nname="pyshacl-turbo"\nversion="{actual_version}"\n'.encode()
    with tarfile.open(archive, "w:gz") as output:
        member = tarfile.TarInfo("package/pyproject.toml")
        member.size = len(data)
        output.addfile(member, io.BytesIO(data))
    sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    entry = {"filename": archive.name, "packagetype": "sdist", "digests": {"sha256": sha}}
    requested = []

    def metadata(version, *, project):
        requested.append((project, version))
        return {"info": {"name": project, "version": version}, "urls": [entry]}

    def download(entry, directory):
        target = directory / entry["filename"]
        shutil.copyfile(archive, target)
        registry.verify_original(target, entry["digests"]["sha256"])
        return target

    monkeypatch.setattr(registry, "metadata", metadata)
    monkeypatch.setattr(registry, "download", download)
    monkeypatch.setattr(module, "load", lambda name: registry)
    if actual_version != "0.6.1":
        with pytest.raises(ValueError, match="locked registry identity"):
            module.original_peer("pyshacl-turbo", "0.6.1", tmp_path / "inputs")
    else:
        record = module.original_peer("pyshacl-turbo", "0.6.1", tmp_path / "inputs")
        assert record["sha256"] == sha
        assert record["project"] == "pyshacl-turbo"
        assert record["version"] == "0.6.1"
        assert "pyproject.toml" in record["files"]
    assert requested == [("pyshacl-turbo", "0.6.1")]


@pytest.mark.parametrize("provider_path", ["../rdflib-turbo", "../rdflib-turbo-other"])
def test_restore_keeps_original_declaration_peer_distinct_from_current_acceptance(
    tmp_path, monkeypatch, provider_path
):
    module = helper()
    native = owner(tmp_path)
    current = tmp_path / "current-acceptance"
    current.mkdir()
    (current / "pyproject.toml").write_text(
        '[project]\nname="pyshacl-turbo"\nversion="0.6.2"\n'
        '[tool.uv.sources]\nrdflib-turbo={path="../rdflib-turbo",editable=true}\n'
    )
    declared = tmp_path / "original-facade"
    declared.mkdir()
    (declared / "pyproject.toml").write_text(
        '[project]\nname="pyshacl-turbo"\nversion="0.6.1"\n'
        f'[tool.uv.sources]\nrdflib-turbo={{path="{provider_path}",editable=true}}\n'
    )
    owl = tmp_path / "original-owl"
    owl.mkdir()
    calls = []

    def original(project, version, output, **kwargs):
        calls.append((project, version))
        if project == "owlrl-turbo":
            assert kwargs == {"owner": native}
        return {"source": str(declared if project == "pyshacl-turbo" else owl), "version": version}

    monkeypatch.setattr(module, "original_peer", original)
    if provider_path != "../rdflib-turbo":
        with pytest.raises(ValueError, match="native source peer"):
            module.restore(native, current, tmp_path)
        assert native.is_dir()
    else:
        result = module.restore(native, current, tmp_path)
        provider = Path(result["provider_source"])
        peer = Path(result["declaration_peer"]["source"])
        assert provider == tmp_path / "cohort/rdflib-turbo"
        assert peer == tmp_path / "cohort/pyshacl-turbo"
        assert peer != current
        assert (current / "pyproject.toml").read_text().count('version="0.6.2"') == 1
        assert calls == [("pyshacl-turbo", "0.6.1"), ("owlrl-turbo", "0.1.0a3")]


def test_original_owl_wheel_and_archive_come_from_the_same_retained_registry_record(
    tmp_path, monkeypatch
):
    module = helper()
    registry = module.load("provider_registry")
    archive = tmp_path / "owlrl_turbo-0.1.0a3.tar.gz"
    data = b'[project]\nname="owlrl-turbo"\nversion="0.1.0a3"\n'
    with tarfile.open(archive, "w:gz") as output:
        member = tarfile.TarInfo("package/pyproject.toml")
        member.size = len(data)
        output.addfile(member, io.BytesIO(data))
    wheel = tmp_path / "owlrl_turbo-0.1.0a3-py3-none-any.whl"
    wheel.write_bytes(b"exact original wheel passed to the verified owner")
    entries = [
        {
            "filename": path.name,
            "packagetype": kind,
            "digests": {"sha256": hashlib.sha256(path.read_bytes()).hexdigest()},
        }
        for path, kind in ((archive, "sdist"), (wheel, "bdist_wheel"))
    ]
    document = {"info": {"name": "owlrl-turbo", "version": "0.1.0a3"}, "urls": entries}
    events = []

    def metadata(version, *, project):
        events.append(("registry", project, version))
        return document

    def download(entry, directory):
        events.append(("download", entry["filename"]))
        source = archive if entry["packagetype"] == "sdist" else wheel
        target = directory / entry["filename"]
        shutil.copyfile(source, target)
        registry.verify_original(target, entry["digests"]["sha256"])
        return target

    def verify_payload(source, original_wheel):
        events.append(("owner-payload", source, original_wheel))
        assert original_wheel.read_bytes() == wheel.read_bytes()
        return {"owlrl_turbo/__init__.py": "d" * 64}

    monkeypatch.setattr(registry, "metadata", metadata)
    monkeypatch.setattr(registry, "download", download)
    monkeypatch.setattr(module, "load", lambda name: registry)
    owner = tmp_path / "verified-provider"
    monkeypatch.setattr(
        module,
        "load_companion",
        lambda actual: SimpleNamespace(verify_payload=verify_payload) if actual == owner else None,
    )
    record = module.original_peer("owlrl-turbo", "0.1.0a3", tmp_path / "inputs", owner=owner)
    assert record["sha256"] == entries[0]["digests"]["sha256"]
    assert record["wheel_sha256"] == entries[1]["digests"]["sha256"]
    assert record["package_payload"] == {"owlrl_turbo/__init__.py": "d" * 64}
    assert Path(record["wheel"]).read_bytes() == wheel.read_bytes()
    assert events[:3] == [
        ("registry", "owlrl-turbo", "0.1.0a3"),
        ("download", archive.name),
        ("download", wheel.name),
    ]
    assert len([event for event in events if event[0] == "registry"]) == 1
