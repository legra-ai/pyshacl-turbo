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
        owner, facade, wheel, owlrl, output, "3.13", owlrl_wheel=owl_wheel
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
