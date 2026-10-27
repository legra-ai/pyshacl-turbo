"""Provider identity cannot use an external or incomplete engine source."""

import importlib.util
from pathlib import Path

import pytest


def module():
    spec = importlib.util.spec_from_file_location(
        "provider_identity", Path(__file__).resolve().parents[1] / "scripts/provider_identity.py"
    )
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


@pytest.mark.parametrize(
    "source,path", [("git+https://example.invalid/x", "crates/engine"), (None, "outside")]
)
def test_metadata_cannot_substitute_external_engine_authority(tmp_path, source, path):
    metadata = {
        "resolve": {"nodes": []},
        "packages": [
            {
                "name": "pyshacl-turbo-engine",
                "source": source,
                "manifest_path": str(tmp_path / path / "Cargo.toml"),
            }
        ],
    }
    with pytest.raises(ValueError, match="archive-owned local SHACL engine"):
        module().derive(tmp_path, metadata)


def test_fingerprint_inventory_must_include_every_owned_implementation(tmp_path):
    root = tmp_path / "crates/engine"
    (root / "src").mkdir(parents=True)
    (root / "Cargo.toml").write_text('[package]\nname="pyshacl-turbo-engine"\n')
    (root / "src/revision.rs").write_text('include_bytes!("revision.rs");\nfn update_source() {}\n')
    (root / "src/omitted.rs").write_text("// executable implementation\n")
    metadata = {
        "resolve": {"nodes": []},
        "packages": [
            {
                "name": "pyshacl-turbo-engine",
                "source": None,
                "manifest_path": str(root / "Cargo.toml"),
            }
        ],
    }
    with pytest.raises(ValueError, match="complete engine implementation"):
        module().derive(tmp_path, metadata)


def test_matcher_is_a_mandatory_semantic_fork_and_its_bytes_change_identity(tmp_path):
    helper = module()
    assert "fancy-regex" in helper.FORKS
    (tmp_path / "vendor").mkdir()
    (tmp_path / "vendor/turbo-source-identity.rs").write_text("// shared identity\n")
    fork = tmp_path / "vendor/fancy-regex-0.19.2"
    (fork / "src").mkdir(parents=True)
    (fork / "Cargo.toml").write_text('[package]\nname="fancy-regex"\n')
    (fork / "build.rs").write_text("fn main() {}\n")
    source = fork / "src/vm.rs"
    source.write_text("// original matcher implementation\n")
    package = {"name": "fancy-regex", "manifest_path": str(fork / "Cargo.toml"), "source": None}
    baseline = helper.fork_identity(tmp_path, package, ["python-re", "std"])
    source.write_text("// changed matcher implementation\n")
    assert helper.fork_identity(tmp_path, package, ["python-re", "std"]) != baseline
    source.write_text("// original matcher implementation\n")
    assert helper.fork_identity(tmp_path, package, ["std", "python-re"]) == baseline
    assert helper.fork_identity(tmp_path, package, ["std"]) != baseline
