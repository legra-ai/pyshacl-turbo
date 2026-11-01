"""Published coverage inputs must be exact original registry files."""

import hashlib
import importlib.util
import io
import tarfile
import tomllib
from pathlib import Path

import pytest
from packaging.version import Version


def module():
    spec = importlib.util.spec_from_file_location(
        "provider_registry", Path(__file__).resolve().parents[1] / "scripts/provider_registry.py"
    )
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_provider_requirement_is_an_exact_runtime_pin(tmp_path):
    path = tmp_path / "pyproject.toml"
    path.write_text('[project]\ndependencies=["rdflib>=7", "rdflib-turbo==0.2.0a9"]\n')
    assert module().declared_version(path) == "0.2.0a9"


def test_facade_pins_the_published_shared_engine_for_runtime_and_tests(canonical_release_project):
    manifest = canonical_release_project / "pyproject.toml"
    version = module().declared_version(manifest)
    # a24 includes the native focus/report ordering correction used by the facade.
    assert Version(version) >= Version("0.2.0a24")
    project = tomllib.loads(manifest.read_text())["project"]
    test_pins = [
        requirement
        for requirement in project["optional-dependencies"]["test"]
        if requirement.startswith("rdflib-turbo")
    ]
    assert test_pins == [f"rdflib-turbo=={version}"]


def test_root_lock_retains_the_declared_registry_provider(canonical_release_project):
    root = canonical_release_project
    lock = tomllib.loads((root / "uv.lock").read_text())
    providers = [package for package in lock["package"] if package["name"] == "rdflib-turbo"]
    assert len(providers) == 1
    assert providers[0]["version"] == module().declared_version(root / "pyproject.toml")
    assert providers[0]["source"] == {"registry": "https://pypi.org/simple"}


@pytest.mark.parametrize("project", ["rdflib-turbo", "pyshacl-turbo", "owlrl-turbo"])
def test_locked_companion_source_requires_one_exact_registry_archive(project):
    registry = module()
    source = {"packagetype": "sdist", "filename": project.replace("-", "_") + "-1.0.0.tar.gz"}
    document = {"info": {"name": project, "version": "1.0.0"}, "urls": [source]}
    assert registry.select_source(document, project, "1.0.0") == source
    with pytest.raises(ValueError, match="exact companion"):
        registry.select_source(document, project, "1.0.1")
    document["urls"].append(source)
    with pytest.raises(ValueError, match="one original source"):
        registry.select_source(document, project, "1.0.0")


@pytest.mark.parametrize("requirement", ["rdflib-turbo>=0.2", "rdflib-turbo @ file:/x", ""])
def test_nonexact_or_absent_provider_pin_is_rejected(tmp_path, requirement):
    path = tmp_path / "pyproject.toml"
    path.write_text(f'[project]\ndependencies=["{requirement}"]\n')
    with pytest.raises(ValueError, match="exact runtime provider pin"):
        module().declared_version(path)


def test_matching_wheel_uses_all_compressed_platform_tags():
    tags = {"cp313-cp313-manylinux_2_17_x86_64", "cp313-cp313-manylinux2014_x86_64"}
    filename = "rdflib_turbo-1.0.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
    assert module().wheel_tags(filename) == tags


def test_original_registry_file_rejects_wrong_sha_and_does_not_replace_bytes(tmp_path):
    path = tmp_path / "original.whl"
    path.write_bytes(b"original")
    module().verify_original(path, hashlib.sha256(b"original").hexdigest())
    with pytest.raises(ValueError, match="original registry file"):
        module().verify_original(path, "0" * 64)
    assert path.read_bytes() == b"original"


def test_registry_selection_rejects_ambiguous_original_wheels():
    tags = {"cp313-cp313-linux_x86_64"}
    document = {
        "info": {"name": "rdflib-turbo", "version": "1.0.0"},
        "urls": [
            {"packagetype": "sdist", "filename": "rdflib_turbo-1.0.0.tar.gz"},
            {
                "packagetype": "bdist_wheel",
                "filename": "rdflib_turbo-1.0.0-cp313-cp313-linux_x86_64.whl",
            },
            {
                "packagetype": "bdist_wheel",
                "filename": "rdflib_turbo-1.0.0-1-cp313-cp313-linux_x86_64.whl",
            },
        ],
    }
    with pytest.raises(ValueError, match="one original source archive and selected wheel"):
        module().select(document, "1.0.0", tags)


@pytest.mark.parametrize("name,kind", [("../escape", "file"), ("package/link", "link")])
def test_original_source_extraction_rejects_escaping_or_link_members(tmp_path, name, kind):
    path = tmp_path / "original.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        member = tarfile.TarInfo(name)
        if kind == "link":
            member.type = tarfile.SYMTYPE
            member.linkname = "/outside"
            archive.addfile(member)
        else:
            member.size = 3
            archive.addfile(member, io.BytesIO(b"bad"))
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="source archive member"):
        module().extract(path, tmp_path / "unpacked", sha)
    assert not (tmp_path / "escape").exists()


def test_original_source_extraction_preserves_bytes_without_git(tmp_path):
    path = tmp_path / "original.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        member = tarfile.TarInfo("package/nested/source.py")
        member.size = 8
        archive.addfile(member, io.BytesIO(b"original"))
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    root = module().extract(path, tmp_path / "unpacked", sha)
    assert (root / "nested/source.py").read_bytes() == b"original"
    assert not (root / ".git").exists()
    record = module().verify_extracted(path, root, sha)
    assert record == {"nested/source.py": hashlib.sha256(b"original").hexdigest()}
    (root / "nested/source.py").write_bytes(b"changed")
    with pytest.raises(ValueError, match="Source bytes differ"):
        module().verify_extracted(path, root, sha)


def test_postbuild_verification_does_not_walk_generated_output(tmp_path, monkeypatch):
    path = tmp_path / "original.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        member = tarfile.TarInfo("package/source.py")
        member.size = 8
        archive.addfile(member, io.BytesIO(b"original"))
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    root = module().extract(path, tmp_path / "unpacked", sha)
    original = Path.rglob

    def rglob(self, pattern):
        if self == root:
            pytest.fail("postbuild verification traversed generated Cargo output")
        return original(self, pattern)

    monkeypatch.setattr(Path, "rglob", rglob)
    assert module().verify_extracted(path, root, sha, exact_inventory=False)


def test_exact_companion_universal_wheel_selection_has_no_platform_or_latest_guess():
    registry = module()
    source = {"filename": "owlrl_turbo-0.1.0a3.tar.gz", "packagetype": "sdist"}
    wheel = {"filename": "owlrl_turbo-0.1.0a3-py3-none-any.whl", "packagetype": "bdist_wheel"}
    document = {"info": {"name": "owlrl-turbo", "version": "0.1.0a3"}, "urls": [source, wheel]}
    assert registry.select_universal(document, "owlrl-turbo", "0.1.0a3") == wheel
    with pytest.raises(ValueError, match="one original universal"):
        registry.select_universal(
            {**document, "urls": [source, wheel, wheel]}, "owlrl-turbo", "0.1.0a3"
        )
    with pytest.raises(ValueError, match="one original universal"):
        registry.select_universal(
            {
                **document,
                "urls": [source, {**wheel, "filename": "owlrl_turbo-0.1.0a3-cp313-cp313-any.whl"}],
            },
            "owlrl-turbo",
            "0.1.0a3",
        )
