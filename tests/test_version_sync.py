"""Release preparation must keep the uv lock current without dependency upgrades."""

import importlib.util
import subprocess
from pathlib import Path


def test_version_bump_keeps_uv_lock_current(tmp_path):
    root = Path(__file__).parents[1]
    spec = importlib.util.spec_from_file_location("sync_version", root / "scripts/sync_version.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    engine = tmp_path / "crates/engine"
    engine.mkdir(parents=True)
    (engine / "Cargo.toml").write_text(
        '[package.metadata.version-info]\nadditional_files = ["pyproject.toml", "uv.lock"]\n'
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "version-regression"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n'
    )
    subprocess.run(["uv", "lock", "--offline", "--project", str(tmp_path)], check=True)
    module.synchronize(tmp_path, "0.2.0")
    subprocess.run(["uv", "lock", "--check", "--offline", "--project", str(tmp_path)], check=True)


def test_real_project_version_bump_works_with_an_empty_uv_cache(tmp_path, monkeypatch):
    import shutil
    import tomllib

    root = Path(__file__).parents[1]
    (tmp_path / "crates/engine").mkdir(parents=True)
    for name in ("pyproject.toml", "uv.lock", "crates/engine/Cargo.toml"):
        shutil.copyfile(root / name, tmp_path / name)
    before = tomllib.loads((tmp_path / "uv.lock").read_text())
    spec = importlib.util.spec_from_file_location("sync_version", root / "scripts/sync_version.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("UV_CACHE_DIR", str(tmp_path / "empty-cache"))
    module.synchronize(tmp_path, "0.0.999")
    subprocess.run(["uv", "lock", "--check", "--offline", "--project", str(tmp_path)], check=True)
    after = tomllib.loads((tmp_path / "uv.lock").read_text())

    def versions(lock):
        return {(p["name"], p["version"]) for p in lock["package"] if p["name"] != "pyshacl-turbo"}

    assert versions(before) == versions(after)
