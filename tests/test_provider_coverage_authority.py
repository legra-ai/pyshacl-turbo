"""Native measurement must execute the explicitly verified provider collector."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module():
    spec = importlib.util.spec_from_file_location(
        "provider_coverage", ROOT / "scripts/provider_coverage.py"
    )
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


@pytest.mark.parametrize("revision", ["", "main", "a" * 39, "g" * 40])
def test_authority_requires_an_immutable_revision_before_reading_source(tmp_path, revision):
    with pytest.raises(ValueError, match="immutable provider revision"):
        module().verify_owner(tmp_path, revision, "a" * 64)


def test_authority_requires_exact_collector_hash_before_reading_source(tmp_path):
    with pytest.raises(ValueError, match="collector SHA-256"):
        module().verify_owner(tmp_path, "a" * 40, "latest")


def test_collector_invocation_never_substitutes_facade_native_measurement(tmp_path):
    owner, facade, wheel, owlrl, output = [tmp_path / name for name in "pfwor"]
    owl_wheel = tmp_path / "owl.whl"
    command = module().collector_command(
        owner,
        facade,
        wheel,
        owlrl,
        output,
        "3.13",
        owlrl_wheel=owl_wheel,
        yaml_authority=tmp_path / "yaml-inputs.json",
    )
    assert command == [
        "uv",
        "run",
        "--no-project",
        "--python",
        "3.13",
        "python",
        str(owner / "scripts/native_coverage.py"),
        "--python",
        "3.13",
        "--shacl-source",
        str(facade),
        "--shacl-wheel",
        str(wheel),
        "--owlrl-source",
        str(owlrl),
        "--owlrl-wheel",
        str(owl_wheel),
        "--yaml-authority",
        str(tmp_path / "yaml-inputs.json"),
        "--output",
        str(output),
    ]


def test_archive_collector_command_preserves_original_archive_identity(tmp_path):
    owner, facade, wheel, owlrl, output = [tmp_path / name for name in "pfwor"]
    archive = tmp_path / "original.tar.gz"
    command = module().collector_command(
        owner,
        facade,
        wheel,
        owlrl,
        output,
        "3.13",
        archive=archive,
        archive_sha256="a" * 64,
        owlrl_wheel=tmp_path / "owl.whl",
        yaml_authority=tmp_path / "yaml-inputs.json",
    )
    assert command[-4:] == ["--source-archive", str(archive), "--source-sha256", "a" * 64]


def test_candidate_collector_command_preserves_explicit_receipt_and_base(tmp_path):
    owner, facade, wheel, owlrl, output = [tmp_path / name for name in "pfwor"]
    receipt = tmp_path / "candidate-facade/candidate-inputs.json"
    command = module().collector_command(
        owner,
        facade,
        wheel,
        owlrl,
        output,
        "3.13",
        candidate={"receipt": receipt, "facade_revision": "a" * 40},
        owlrl_wheel=tmp_path / "owl.whl",
        yaml_authority=tmp_path / "yaml-inputs.json",
    )
    assert command[-4:] == [
        "--shacl-candidate-receipt",
        str(receipt),
        "--shacl-base-revision",
        "a" * 40,
    ]
    with pytest.raises(ValueError, match="published provider"):
        module().collector_command(
            owner,
            facade,
            wheel,
            owlrl,
            output,
            "3.13",
            archive=tmp_path / "archive.tar.gz",
            archive_sha256="b" * 64,
            candidate={"receipt": receipt, "facade_revision": "a" * 40},
            owlrl_wheel=tmp_path / "owl.whl",
            yaml_authority=tmp_path / "yaml-inputs.json",
        )


def test_published_owl_command_retains_both_original_archive_fields(tmp_path):
    owner, facade, wheel, owlrl, output = [tmp_path / name for name in "pfwor"]
    archive = tmp_path / "owlrl_turbo-0.1.0a3.tar.gz"
    command = module().collector_command(
        owner,
        facade,
        wheel,
        owlrl,
        output,
        "3.13",
        owlrl_archive=archive,
        owlrl_sha256="d" * 64,
        owlrl_wheel=tmp_path / "owl.whl",
        yaml_authority=tmp_path / "yaml-inputs.json",
    )
    assert command[-4:] == ["--owlrl-archive", str(archive), "--owlrl-sha256", "d" * 64]
    with pytest.raises(ValueError, match="Both OWL source archive and SHA"):
        module().freeze_owl_source(tmp_path, archive, None)


@pytest.mark.parametrize(
    "revision,archive,sha",
    [(None, None, None), ("a" * 40, "archive", "b" * 64), (None, "archive", None)],
)
def test_source_authority_modes_are_explicit_and_disjoint(tmp_path, revision, archive, sha):
    with pytest.raises(ValueError, match="exactly one complete provider source authority"):
        module().verify_source(tmp_path, revision, "c" * 64, archive, sha)


def test_collector_requires_an_explicit_yaml_authority(tmp_path):
    with pytest.raises(TypeError, match="yaml_authority"):
        module().collector_command(
            tmp_path,
            tmp_path,
            tmp_path,
            tmp_path,
            tmp_path,
            "3.13",
            owlrl_wheel=tmp_path / "owl.whl",
        )


@pytest.mark.parametrize("damage", [None, "inputs", "proof", "project", "uuid", "venv"])
def test_yaml_summary_is_reattested_in_the_collectors_actual_owned_environment(tmp_path, damage):
    from types import SimpleNamespace

    owner = tmp_path / "owner"
    project = owner / "target/native-coverage/profiles" / ("a" * 32) / "project"
    (project / ".venv").mkdir(parents=True)
    authority = tmp_path / "yaml-inputs.json"
    record = {"kind": "test-only-yaml-dependency", "owner_lock_sha256": "frozen"}
    proof = {"origin": str(project / ".venv/site-packages/yaml"), "opaque": "full-proof"}
    summary = {
        "yaml_inputs": record,
        "yaml_installed": proof,
        "yaml_environment": {"project": str(project), "venv": str(project / ".venv")},
    }
    called = []

    def verify(actual_owner, actual_authority, project_run, venv, environment):
        called.append(True)
        assert actual_owner == owner and actual_authority == authority
        assert project_run == ["uv", "run", "--project", project, "--locked", "--no-sync"]
        assert venv == project / ".venv" and environment == {"ORIGINAL": "1"}
        return proof

    if damage == "inputs":
        summary["yaml_inputs"] = {"substitute": "inputs"}
    elif damage == "proof":
        summary["yaml_installed"] = {"substitute": "proof"}
    elif damage in {"project", "uuid"}:
        bad = (
            tmp_path / "foreign" if damage == "project" else project.parent.parent / "wrong/project"
        )
        (bad / ".venv").mkdir(parents=True)
        summary["yaml_environment"] = {"project": str(bad), "venv": str(bad / ".venv")}
    elif damage == "venv":
        bad = tmp_path / "foreign-venv"
        bad.mkdir()
        summary["yaml_environment"]["venv"] = str(bad)
    collector = SimpleNamespace(verify_installed_yaml=verify)
    if damage:
        with pytest.raises(ValueError, match="YAML"):
            module().verify_yaml_summary(
                owner, authority, record, summary, collector, {"ORIGINAL": "1"}
            )
    else:
        module().verify_yaml_summary(
            owner, authority, record, summary, collector, {"ORIGINAL": "1"}
        )
        assert called == [True]
