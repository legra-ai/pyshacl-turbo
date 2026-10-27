"""The facade ships one universal wheel with no second native library."""

import importlib.util
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def facade_archives(tmp_path_factory):
    output = tmp_path_factory.mktemp("facade-release")
    for source, kind in ((ROOT, "--sdist"), (None, "--wheel")):
        if source is None:
            (source,) = output.glob("*.tar.gz")
        subprocess.run(
            [
                "uv",
                "build",
                kind,
                "--python",
                sys.executable,
                "--out-dir",
                str(output),
                str(source),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    # CI downloads only uploaded archives into the release inventory directory.
    release = output / "release"
    release.mkdir()
    for pattern in ("*.whl", "*.tar.gz"):
        for archive in output.glob(pattern):
            archive.replace(release / archive.name)
    return release


def release_module():
    spec = importlib.util.spec_from_file_location(
        "release_packages", ROOT / "scripts/release_packages.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_actual_facade_archives_pass_the_release_inventory_and_package_checks(facade_archives):
    (wheel,) = facade_archives.glob("*.whl")
    version = wheel.name.split("-")[1]
    if "+" in version:
        with pytest.raises(ValueError, match="Candidate artifacts cannot be published or tagged"):
            release_module().inventory(facade_archives, version)
        packages = list(facade_archives.iterdir())
    else:
        packages = release_module().inventory(facade_archives, version)
    assert {path.name for path in packages} == {
        f"pyshacl_turbo-{version}.tar.gz",
        f"pyshacl_turbo-{version}-py3-none-any.whl",
    }
    for path in packages:
        subprocess.run(
            [sys.executable, "scripts/check_package.py", str(path)], cwd=ROOT, check=True
        )


def test_facade_checker_rejects_an_accidental_second_native_library(facade_archives, tmp_path):
    (wheel,) = facade_archives.glob("*.whl")
    contaminated = tmp_path / wheel.name
    with zipfile.ZipFile(wheel) as original, zipfile.ZipFile(contaminated, "w") as modified:
        for name in original.namelist():
            modified.writestr(name, original.read(name))
        modified.writestr("pyshacl_turbo/_duplicate.so", b"not a shared engine")
    result = subprocess.run(
        [sys.executable, "scripts/check_package.py", str(contaminated)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "must not contain native libraries" in result.stderr


@pytest.mark.parametrize("unexpected", ["extra", "native", "directory"])
def test_facade_release_inventory_rejects_unexpected_entries(tmp_path, unexpected):
    source = tmp_path / "pyshacl_turbo-0.6.1.tar.gz"
    wheel = tmp_path / "pyshacl_turbo-0.6.1-py3-none-any.whl"
    source.write_bytes(b"source")
    wheel.write_bytes(b"wheel")
    if unexpected == "extra":
        (tmp_path / ".unexpected").write_bytes(b"extra")
    elif unexpected == "native":
        wheel.rename(tmp_path / "pyshacl_turbo-0.6.1-cp311-abi3-win_amd64.whl")
    else:
        wheel.unlink()
        wheel.mkdir()
    with pytest.raises(ValueError, match="one universal facade wheel"):
        release_module().inventory(tmp_path, "0.6.1")


def test_candidate_namespace_cannot_enter_release_inventory_or_tag_recovery(tmp_path, monkeypatch):
    version = "0.6.1+candidate.0123456789ab"
    (tmp_path / f"pyshacl_turbo-{version}.tar.gz").write_bytes(b"source")
    (tmp_path / f"pyshacl_turbo-{version}-py3-none-any.whl").write_bytes(b"wheel")
    helper = release_module()
    with pytest.raises(ValueError, match="Candidate artifacts cannot be published or tagged"):
        helper.inventory(tmp_path, version)
    monkeypatch.setattr(
        helper.subprocess,
        "check_output",
        lambda *args, **kwargs: pytest.fail("queried candidate tag"),
    )
    with pytest.raises(ValueError, match="Candidate artifacts cannot be published or tagged"):
        helper.stage(version, "a" * 40)
