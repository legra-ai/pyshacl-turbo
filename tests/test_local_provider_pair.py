"""A source archive checks declarations without assuming a sibling checkout."""

import importlib.util
import tomllib
from pathlib import Path

import pytest


def helper():
    path = Path(__file__).resolve().parents[1] / "scripts/local_provider_pair.py"
    spec = importlib.util.spec_from_file_location("local_provider_pair", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_registry_project_is_not_an_explicit_local_provider_declaration():
    root = Path(__file__).resolve().parents[1]
    manifest = tomllib.loads((root / "pyproject.toml").read_text())
    (requirement,) = [
        text for text in manifest["project"]["dependencies"] if text.startswith("rdflib-turbo==")
    ]
    lock = tomllib.loads((root / "uv.lock").read_text())
    (provider,) = [entry for entry in lock["package"] if entry["name"] == "rdflib-turbo"]
    assert provider["version"] == requirement.split("==")[1]
    assert provider["source"] == {"registry": "https://pypi.org/simple"}
    with pytest.raises(ValueError, match="explicit sibling editable provider declaration"):
        helper().declaration(root)


def paired_fixture(tmp_path):
    facade, provider = tmp_path / "facade", tmp_path / "provider"
    facade.mkdir()
    (provider / "crates/engine/src").mkdir(parents=True)
    (facade / "pyproject.toml").write_text(
        '[project]\nname="pyshacl-turbo"\ndependencies=["rdflib-turbo==1.2.3"]\n'
        '[tool.uv.sources]\nrdflib-turbo={path="../provider",editable=true}\n'
    )
    (facade / "uv.lock").write_text(
        'version=1\n[[package]]\nname="rdflib-turbo"\nversion="1.2.3"\n'
        'source={editable="../provider"}\n'
    )
    (provider / "pyproject.toml").write_text('[project]\nname="rdflib-turbo"\nversion="1.2.3"\n')
    (provider / "Cargo.toml").write_text(
        '[dependencies]\npyshacl-turbo-engine={path="crates/engine"}\n'
    )
    (provider / "crates/engine/src/lib.rs").write_text("// Synthetic native owner fixture.\n")
    return facade, provider


def test_explicit_arranged_provider_owns_the_declared_engine(tmp_path):
    facade, provider = paired_fixture(tmp_path)
    assert helper().verify(facade, provider)["version"] == "1.2.3"


def test_editable_override_uses_locked_source_version_without_changing_registry_pin(tmp_path):
    facade, provider = paired_fixture(tmp_path)
    path = facade / "uv.lock"
    path.write_text(path.read_text().replace('version="1.2.3"', 'version="1.2.4"'))
    path = provider / "pyproject.toml"
    path.write_text(path.read_text().replace('version="1.2.3"', 'version="1.2.4"'))
    actual = helper().verify(facade, provider)
    assert actual["version"] == "1.2.4"
    assert actual["registry_version"] == "1.2.3"


@pytest.mark.parametrize(
    "defect",
    [
        "locked-source",
        "locked-version",
        "provider-name",
        "provider-version",
        "engine-path",
        "missing-engine",
    ],
)
def test_wrong_declaration_or_owner_fails_explicitly(tmp_path, defect):
    facade, provider = paired_fixture(tmp_path)
    if defect == "locked-source":
        path = facade / "uv.lock"
        path.write_text(path.read_text().replace("../provider", "../other"))
    elif defect == "locked-version":
        path = facade / "uv.lock"
        path.write_text(path.read_text().replace('version="1.2.3"', 'version="9.9.9"'))
    elif defect in ("provider-name", "provider-version"):
        path = provider / "pyproject.toml"
        before, after = (
            ("rdflib-turbo", "foreign") if defect == "provider-name" else ("1.2.3", "9.9.9")
        )
        path.write_text(path.read_text().replace(before, after))
    elif defect == "engine-path":
        (provider / "Cargo.toml").write_text(
            '[dependencies]\npyshacl-turbo-engine={path="foreign"}\n'
        )
    else:
        (provider / "crates/engine/src/lib.rs").unlink()
    with pytest.raises((ValueError, FileNotFoundError)):
        helper().verify(facade, provider)
